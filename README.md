# Home Assistant Add-on: Kiwix Server

A Home Assistant add-on that provides a Kiwix server for serving offline Wikipedia and other ZIM files with a built-in management interface.

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

## About

Kiwix is an offline reader for web content, designed to make Wikipedia and other content available without internet access. This add-on provides an easy way to run Kiwix within your Home Assistant environment, with a web-based management interface for managing ZIM files.

### Features

- **Offline Wikipedia**: Serve complete offline Wikipedia and other content
- **Multiple ZIM Files**: Support for serving multiple ZIM files simultaneously
- **Auto-Detection**: Automatically detects new and removed ZIM files without restart
- **Management Interface**: Web-based UI for downloading, uploading, and managing ZIM files
- **Download Progress**: Real-time progress tracking for ZIM file downloads
- **Direct Network Access**: Accessible both via Home Assistant ingress and direct network access
- **Multi-Architecture**: Support for various CPU architectures

## Installation

1. Navigate in your Home Assistant frontend to **Settings** → **Add-ons** → **Add-on Store**.
2. Add this repository by clicking the menu in the top-right and selecting **Repositories**.
3. Add the URL: `https://github.com/MichalTorma/ha-repository`
4. Find the "Kiwix Server" add-on and click it.
5. Click on the "INSTALL" button.

## How to use

1. Configure the add-on according to your needs (see Configuration section).
2. Start the add-on.
3. Access Kiwix through Home Assistant sidebar (ingress) or directly via `http://homeassistant-ip:8111`.
4. Use the Management tab (or `http://homeassistant-ip:8111/manage/`) to add ZIM files.

### Basic Configuration

The default configuration works out of the box:

```yaml
port: 8111
zim_storage_path: "/data/zim"
log_level: "info"
max_upload_size: 10000
enable_management: true
```

**Note**: The `management_port` option has been removed. Both Kiwix and Management are now accessible via the single `port` (8111) using path-based routing:
- `/wiki/` → Kiwix server
- `/manage/` → Management API

### Adding ZIM Files

You can add ZIM files in three ways:

1. **Via Management Interface**: Access `http://homeassistant-ip:8111/manage/` or use the Management tab in the sidebar
2. **Download from URL**: Use the management interface to download ZIM files directly
3. **Upload Files**: Upload ZIM files you've created yourself via the management interface

### Popular ZIM Files

Some popular ZIM files you can download:

- Wikipedia: `https://download.kiwix.org/zim/wikipedia/`
- Wiktionary: `https://download.kiwix.org/zim/wiktionary/`
- Project Gutenberg: `https://download.kiwix.org/zim/gutenberg/`

Visit [kiwix.org](https://www.kiwix.org/en/downloads/) for more ZIM files.

## Configuration

For detailed configuration options, see the [DOCS.md](DOCS.md) file.

## Access Methods

### Via Home Assistant Ingress (Recommended)

Access via Home Assistant sidebar - **fully functional**:
- ✅ Full CSS styling
- ✅ Working JavaScript
- ✅ Complete ZIM file list
- ✅ Functional selectors
- ✅ Tabbed interface (Wiki + Management)

The add-on uses nginx reverse proxy with path rewriting to fix ingress compatibility issues.

### Via Direct Network Access

**Single Port Access:**
- **Landing Page**: `http://homeassistant-ip:8111/` - Tabbed interface
- **Kiwix Wiki**: `http://homeassistant-ip:8111/wiki/` - Direct Kiwix access
- **Management**: `http://homeassistant-ip:8111/manage/` - File management

All features work identically via ingress or direct network access.

## Support

Got questions? Please use the [GitHub Issues][issues] for this repository.

## License

MIT License - see [LICENSE] file for details.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
[issues]: https://github.com/MichalTorma/ha-kiwix/issues
[LICENSE]: https://github.com/MichalTorma/ha-kiwix/blob/main/LICENSE
