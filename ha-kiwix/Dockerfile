# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
FROM ghcr.io/kiwix/kiwix-tools:3.6.0

# # Execute during the build of the image
ARG TEMPIO_VERSION BUILD_ARCH
RUN apk add --no-cache cronie curl
RUN \
    curl -sSLf -o /usr/bin/tempio \
    "https://github.com/home-assistant/tempio/releases/download/${TEMPIO_VERSION}/tempio_${BUILD_ARCH}"

# Copy root filesystem
COPY rootfs /


RUN echo "0 2 * * * /usr/bin/run_kiwix --update" > /etc/crontabs/root
# CMD ["/usr/bin/run_kiwix"]
CMD ["tail", "-f", "/dev/null"]
