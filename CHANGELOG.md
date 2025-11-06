# Changelog

All notable changes to this add-on will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.7] - 2025-01-XX

### Fixed

- Improved ingress path detection using regex pattern matching
- Added JavaScript-based path rewriting for iframe content (fetch/XHR)
- Removed nginx sub_filter variable usage (not supported) in favor of JavaScript rewriting
- Added console logging for debugging ingress path detection
- Fixed duplicate MIME type warning in nginx config

## [1.2.6] - 2025-01-XX

### Fixed

- Fixed management API not seeing ZIM files when accessed via ingress
- Updated management API JavaScript to detect and use ingress path for API calls
- Fixed Kiwix CSS and data not loading via ingress by improving ingress path detection
- Ingress path is now extracted from request URI when header is not available
- Both Kiwix wiki and management interface now work correctly via ingress

## [1.2.5] - 2025-01-XX

### Fixed

- Fixed 404 errors when accessing via Home Assistant ingress sidebar
- Updated nginx location blocks to handle ingress paths (e.g., `/632709b9_kiwix/ingress/wiki/`)
- Updated landing page HTML to detect and use ingress path for iframe URLs
- Both direct network access and ingress access now work correctly

## [1.2.4] - 2025-01-XX

### Fixed

- Fixed redirect issue when clicking ZIM files - Kiwix was redirecting to `/viewer` without `/wiki/` prefix
- Added sub_filter rules to rewrite `/viewer` URLs to `/wiki/viewer` in HTML/JavaScript responses
- ZIM file viewer now works correctly when accessed via `/wiki/` path

## [1.2.3] - 2025-01-XX

### Fixed

- Fixed 404 error when clicking on ZIM files - added `/viewer` endpoint to Kiwix API routing
- ZIM file viewer now works correctly when accessed via direct network or ingress

## [1.2.2] - 2025-01-XX

### Fixed

- Fixed 404 errors for API requests from iframes (Kiwix catalog endpoints and Management API)
- Added location blocks to catch absolute path API requests (`/api/`, `/catalog/`, etc.)
- Fixed routing so API calls work correctly from both direct access and ingress
- Fixed duplicate MIME type warning in nginx config

## [1.2.1] - 2025-01-XX

### Fixed

- Fixed startup failure due to removed `management_port` configuration check
- Removed obsolete port conflict check from requirements script

## [1.2.0] - 2025-01-XX

### Added

- **BREAKING**: Added nginx reverse proxy for proper ingress support
- Unified interface accessible via single port (8111) with path-based routing
- Tabbed landing page combining Kiwix Wiki and Management interfaces
- `/wiki/` path for Kiwix server (with ingress path rewriting for CSS/assets)
- `/manage/` path for Management API
- Full ingress support - CSS, JavaScript, and all features now work via sidebar
- Both services accessible via direct network access or ingress

### Changed

- **BREAKING**: Removed separate `management_port` configuration option
- Management API now runs on internal port 8081 (proxied via nginx)
- Kiwix server runs on internal port 8080 (proxied via nginx)
- Only port 8111 is exposed externally (nginx handles routing)
- Landing page provides tabbed interface to switch between Wiki and Management

### Fixed

- Fixed CSS and asset loading issues when accessed via Home Assistant ingress
- Fixed empty selectors issue in Kiwix interface via ingress
- Proper path rewriting for Kiwix's absolute asset paths
- All features now work correctly via ingress

### Technical

- Nginx reverse proxy handles path rewriting for ingress compatibility
- Uses `sub_filter` to rewrite absolute paths in HTML/CSS/JS responses
- Detects ingress path from `X-Ingress-Path` header
- Both direct network access and ingress access fully supported

## [1.1.5] - 2025-01-XX

### Documentation

- Enhanced documentation about ingress limitations
- Clarified that Kiwix via ingress has limited functionality (no CSS, empty selectors)
- Added clear recommendation to use direct network access for best experience
- Explained why ingress doesn't work well with Kiwix (absolute asset paths)

## [1.1.4] - 2025-01-XX

### Fixed

- Fixed ZIM files not being added to library.xml after download/upload
- Management API now uses `kiwix-manage` to add/remove ZIM files from library.xml
- ZIM files are now automatically detected by Kiwix server after download/upload
- Fixed library.xml not being updated when files are added

## [1.1.3] - 2025-01-XX

### Fixed

- Fixed grep command error (removed Perl regex -P flag for BusyBox compatibility)
- Improved IP address detection using BusyBox-compatible commands
- Added reminder about enabling ports in add-on Network settings

## [1.1.2] - 2025-01-XX

### Fixed

- Fixed hostname command error (BusyBox compatibility)
- Improved IP address detection for management API URL logging

## [1.1.1] - 2025-01-XX

### Fixed

- Explicitly set management API to bind to 0.0.0.0 for network access
- Added better logging for management API accessibility
- Added note about Kiwix CSS limitations with ingress (absolute paths)

### Known Issues

- Kiwix may show unstyled HTML when accessed via ingress due to absolute asset paths
- Recommended to use direct network access for best experience: `http://homeassistant-ip:8111`

## [1.1.0] - 2025-01-XX

### Changed

- **BREAKING**: Changed default ports from 8080/8081 to 8111/8112
  - Kiwix server default port: 8111
  - Management API default port: 8112
  - Updated ingress_port to match new default (8111)
- Simplified port configuration - removed alternative port mappings

## [1.0.6] - 2025-01-XX

### Fixed

- Added ports 8180 and 8181 to exposed ports for alternative configurations
- Added warning when configured port doesn't match ingress_port
- Improved documentation about ingress port limitations

## [1.0.5] - 2025-01-XX

### Fixed

- Added port 8082 to exposed ports for management API
- Fixed port exposure issue when management API uses port 8082
- Added note about ingress_port needing to match 'port' option

## [1.0.4] - 2025-01-XX

### Improved

- Added clarifying comment about port configuration
- Ports section now properly documented to match options defaults

## [1.0.3] - 2025-01-XX

### Improved

- Added health check verification for management API startup
- Improved logging for management API status verification
- Increased wait time for management API to fully start

## [1.0.2] - 2025-01-XX

### Fixed

- Fixed restart loop when no ZIM files are present by creating empty library.xml file
- Kiwix server now starts successfully even with empty ZIM storage directory
- Added proper handling for empty library state

## [1.0.1] - 2025-01-XX

### Fixed

- Fixed Python package installation by using virtual environment to comply with PEP 668
- Updated Dockerfile to create virtual environment before installing Python dependencies
- Fixed service script to use virtual environment Python interpreter

## [1.0.0] - 2025-01-XX

### Added

- Initial release of Kiwix Server add-on
- Support for serving offline Wikipedia and other ZIM files
- Multiple ZIM file support with automatic detection
- Web-based management interface for file operations
- Download ZIM files from URLs with progress tracking
- Upload ZIM files from local computer
- Delete ZIM files via management interface
- Real-time download progress monitoring
- Home Assistant ingress support
- Direct network access support
- Automatic ZIM file detection using `--monitorLibrary`
- Comprehensive logging with configurable log levels
- Multi-architecture support (amd64, aarch64, armv7, armhf, i386)
- Configurable ports for server and management interface
- Configurable storage path and upload size limits
- Health checks and service monitoring
- Production-ready configuration
- Comprehensive documentation

### Features

- **Kiwix Server**: Runs on port 8111 with `--library` and `--monitorLibrary` options
- **Management API**: FastAPI-based REST API on port 8112
- **Management UI**: Modern web interface for managing ZIM files
- **Progress Tracking**: Real-time progress for downloads and uploads
- **Auto-Detection**: Automatically detects new/removed ZIM files without restart

### Security

- Non-root user execution for enhanced security
- File upload validation and size limits
- Secure file operations with proper permissions
- Input validation and sanitization

### Documentation

- Complete setup and configuration guide
- Management interface usage instructions
- Troubleshooting guide
- API documentation
- Popular ZIM file sources

