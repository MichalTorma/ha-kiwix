FROM ghcr.io/hassio-addons/base:15.0.7

# Install dependencies
RUN apk add --no-cache cronie curl py3-pip \

# Install requests
RUN pip install requests

# Specify build arguments
ARG BUILD_ARCH
ARG KIWIX_TOOLS_VERSION="3.1.2"

# Install Kiwix-tools based on architecture
RUN if [ "${BUILD_ARCH}" = "amd64" ]; then \
        KIWIX_ARCH="x86_64"; \
    elif [ "${BUILD_ARCH}" = "aarch64" ]; then \
        KIWIX_ARCH="arm64"; \
    elif [ "${BUILD_ARCH}" = "armv7" ]; then \
        KIWIX_ARCH="armhf"; \
    else \
        KIWIX_ARCH=$BUILD_ARCH; \
    fi && \
        curl -L "https://download.kiwix.org/release/kiwix-tools/kiwix-tools_linux-${KIWIX_ARCH}-${KIWIX_TOOLS_VERSION}.tar.gz" | tar -xz -C /usr/local/bin --strip-components=1; \


EXPOSE 8080

# Setup cron job
RUN echo "0 2 * * * /usr/local/bin/kiwix-serve --update" > /etc/crontabs/root

# Define default command
CMD ["/usr/local/bin/kiwix-serve --start"]
