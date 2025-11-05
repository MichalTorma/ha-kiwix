# Changelog

All notable changes to this add-on will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

