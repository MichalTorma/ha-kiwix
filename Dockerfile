ARG BUILD_FROM
FROM $BUILD_FROM

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Build arguments
ARG BUILD_ARCH

# Install base dependencies and build dependencies for nginx-lua-module
RUN \
    apk add --no-cache \
        ca-certificates \
        tzdata \
        curl \
        wget \
        bash \
        python3 \
        py3-pip \
        jq \
        nginx \
        lua5.1 \
        lua5.1-dev \
        luajit \
        luajit-dev

# Build and install nginx lua module from source
RUN \
    apk add --no-cache --virtual .build-deps \
        build-base \
        linux-headers \
        openssl-dev \
        pcre-dev \
        zlib-dev \
        nginx \
        git \
    && mkdir -p /tmp/build \
    && cd /tmp/build \
    # Download ngx_devel_kit
    && wget https://github.com/vision5/ngx_devel_kit/archive/v0.3.3.tar.gz -O ndk.tar.gz \
    && tar -xzf ndk.tar.gz \
    && NDK_DIR=$(pwd)/ngx_devel_kit-0.3.3 \
    # Download lua-nginx-module
    && wget https://github.com/openresty/lua-nginx-module/archive/v0.10.26.tar.gz -O lua-nginx.tar.gz \
    && tar -xzf lua-nginx.tar.gz \
    && LUA_DIR=$(pwd)/lua-nginx-module-0.10.26 \
    # Get nginx version and configuration (BusyBox-compatible)
    && NGINX_VERSION=$(nginx -v 2>&1 | sed -n 's/.*nginx\/\([0-9.]*\).*/\1/p') \
    && echo "Detected nginx version: ${NGINX_VERSION}" \
    # Get nginx configure arguments to ensure compatibility
    && NGINX_ARGS=$(nginx -V 2>&1 | grep "configure arguments:" | sed 's/configure arguments://') \
    && echo "Nginx configure args: ${NGINX_ARGS}" \
    && wget http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz \
    && tar -xzf nginx-${NGINX_VERSION}.tar.gz \
    && cd nginx-${NGINX_VERSION} \
    # Configure with same args as installed nginx, adding our dynamic modules
    && export LUAJIT_LIB=/usr/lib \
    && export LUAJIT_INC=/usr/include/luajit-2.1 \
    && ./configure ${NGINX_ARGS} \
        --add-dynamic-module=${NDK_DIR} \
        --add-dynamic-module=${LUA_DIR} \
    && make modules \
    # Install modules
    && mkdir -p /usr/lib/nginx/modules \
    && cp objs/ndk_http_module.so /usr/lib/nginx/modules/ \
    && cp objs/ngx_http_lua_module.so /usr/lib/nginx/modules/ \
    # Verify modules
    && ls -lah /usr/lib/nginx/modules/ \
    # Cleanup
    && cd / \
    && rm -rf /tmp/build \
    && apk del .build-deps

# Install Kiwix tools
# Try to install from Alpine repos first, fallback to building from source
RUN \
    if apk add --no-cache kiwix-tools 2>/dev/null; then \
        echo "Kiwix tools installed from Alpine repos"; \
    else \
        echo "Kiwix tools not in repos, building from source..." && \
        apk add --no-cache --virtual .build-deps \
            build-base \
            cmake \
            git \
            libzim-dev \
            zlib-dev \
            xz-dev \
            libmicrohttpd-dev \
            libcurl \
            libmagic-dev && \
        git clone --depth 1 https://github.com/kiwix/kiwix-tools.git /tmp/kiwix-tools && \
        cd /tmp/kiwix-tools && \
        mkdir build && cd build && \
        cmake -DCMAKE_BUILD_TYPE=Release .. && \
        make -j$(nproc) && \
        make install && \
        cd / && \
        rm -rf /tmp/kiwix-tools && \
        apk del .build-deps; \
    fi

# Create kiwix user and directories first
RUN \
    addgroup -g 1000 kiwix \
    && adduser -D -s /bin/bash -u 1000 -G kiwix kiwix \
    && mkdir -p /data/zim \
    && mkdir -p /var/log/kiwix \
    && mkdir -p /opt/venv

# Install Python dependencies for management API in virtual environment
RUN \
    python3 -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        fastapi==0.104.1 \
        uvicorn[standard]==0.24.0 \
        python-multipart==0.0.6 \
        aiofiles==23.2.1

# Create nginx directories
RUN \
    mkdir -p /var/log/nginx \
    && mkdir -p /usr/share/nginx/html \
    && mkdir -p /etc/nginx

# Set permissions
RUN \
    chown -R kiwix:kiwix /data \
    && chown -R kiwix:kiwix /var/log/kiwix \
    && chown -R kiwix:kiwix /opt/venv \
    && chown -R nginx:nginx /var/log/nginx \
    && chown -R nginx:nginx /usr/share/nginx/html \
    && chmod -R g+w /data

# Copy rootfs
COPY rootfs /

# Set proper permissions on scripts
RUN \
    chmod +x /etc/cont-init.d/*.sh \
    && chmod +x /etc/services.d/kiwix/run \
    && chmod +x /etc/services.d/kiwix/finish \
    && chmod +x /usr/local/bin/kiwix-manager.py

# Build arguments for labels
ARG BUILD_DATE
ARG BUILD_DESCRIPTION
ARG BUILD_NAME
ARG BUILD_REF
ARG BUILD_REPOSITORY
ARG BUILD_VERSION

# Labels
LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="Michal Torma <torma.michal@gmail.com>" \
    org.opencontainers.image.title="${BUILD_NAME}" \
    org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
    org.opencontainers.image.vendor="Home Assistant Community Add-ons" \
    org.opencontainers.image.authors="Michal Torma <torma.michal@gmail.com>" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://github.com/MichalTorma/ha-kiwix" \
    org.opencontainers.image.source="https://github.com/${BUILD_REPOSITORY}" \
    org.opencontainers.image.documentation="https://github.com/${BUILD_REPOSITORY}/blob/main/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}

# Expose ports
EXPOSE 8111

# Set working directory
WORKDIR /data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8111 || exit 1

