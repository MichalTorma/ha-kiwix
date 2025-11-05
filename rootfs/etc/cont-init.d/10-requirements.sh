#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Community Add-on: Kiwix
# This files check if all user configuration requirements are met
# ==============================================================================

bashio::log.info "Checking add-on requirements..."

# Check if Kiwix tools are available
if ! command -v kiwix-serve &> /dev/null; then
    bashio::exit.nok "kiwix-serve command not found. Kiwix tools may not be installed correctly."
fi

bashio::log.info "Kiwix tools found: $(kiwix-serve --version 2>&1 || echo 'version check failed')"

# Check port configuration
PORT=$(bashio::config 'port')
MANAGEMENT_PORT=$(bashio::config 'management_port')

if (( PORT == MANAGEMENT_PORT )); then
    bashio::exit.nok "Kiwix server port and management port must be different!"
fi

# Check ZIM storage path
ZIM_STORAGE_PATH=$(bashio::config 'zim_storage_path')
if bashio::var.is_empty "${ZIM_STORAGE_PATH}"; then
    bashio::exit.nok "ZIM storage path must be configured!"
fi

# Check max upload size
MAX_UPLOAD_SIZE=$(bashio::config 'max_upload_size')
if (( MAX_UPLOAD_SIZE < 1 )); then
    bashio::exit.nok "Max upload size must be at least 1 MB!"
fi

bashio::log.info "Add-on requirements check completed successfully!"

