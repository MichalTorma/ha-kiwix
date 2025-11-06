# Home Assistant Add-on: Kiwix Server

A Kiwix server for serving offline Wikipedia and other ZIM files with a built-in management interface.

## Installation

1. Navigate to **Settings** → **Add-ons** → **Add-on Store** in your Home Assistant frontend.
2. Add this repository if not already added.
3. Install the "Kiwix Server" add-on.
4. Configure the add-on (see configuration options below).
5. Start the add-on.

## Configuration

Add-on configuration:

```yaml
port: 8111
management_port: 8112
zim_storage_path: "/data/zim"
log_level: "info"
max_upload_size: 10000
enable_management: true
```

### Configuration Options

#### Server Configuration

- **port**: Port for nginx reverse proxy (default: `8111`)
  - This is the single external port that handles both Kiwix and Management
  - Accessible via Home Assistant ingress and direct network access
  - Routes:
    - `/wiki/` → Kiwix server
    - `/manage/` → Management API
    - `/` → Landing page with tabs

- **zim_storage_path**: Path where ZIM files are stored (default: `/data/zim`)
  - Files stored here will be automatically detected by Kiwix
  - Must be a writable directory

#### Logging

- **log_level**: Logging verbosity level (`debug`, `info`, `warning`, `error`)
  - `debug`: Most verbose, shows detailed information
  - `info`: Standard logging (default)
  - `warning`: Only warnings and errors
  - `error`: Only errors

#### File Management

- **max_upload_size**: Maximum upload size in MB (default: `10000`)
  - Limits the size of ZIM files that can be uploaded via the management interface
  - Large ZIM files (like full Wikipedia) can be several GB

- **enable_management**: Enable the management interface (default: `true`)
  - Set to `false` to disable the management API and UI
  - Kiwix server will still work, but you won't be able to manage files via the web interface

## Using the Management Interface

The management interface is available at `http://homeassistant-ip:8112` when the add-on is running.

### Features

1. **List ZIM Files**: View all available ZIM files with size and modification date
2. **Download ZIM Files**: Download ZIM files from URLs with progress tracking
3. **Upload ZIM Files**: Upload ZIM files from your local computer
4. **Delete ZIM Files**: Remove ZIM files you no longer need

### Downloading ZIM Files

1. Access the management interface at `http://homeassistant-ip:8112`
2. Enter the URL of a ZIM file in the "Download ZIM File from URL" section
3. Click "Download"
4. Monitor progress in the progress bar
5. Once complete, the file will automatically appear in Kiwix

Popular ZIM file sources:
- Kiwix download site: `https://download.kiwix.org/zim/`
- Wikipedia: `https://download.kiwix.org/zim/wikipedia/`
- Wiktionary: `https://download.kiwix.org/zim/wiktionary/`

### Uploading ZIM Files

1. Access the management interface at `http://homeassistant-ip:8112`
2. Click "Choose File" in the "Upload ZIM File" section
3. Select a `.zim` file from your computer
4. Click "Upload"
5. Monitor upload progress
6. Once complete, the file will automatically appear in Kiwix

### Deleting ZIM Files

1. Access the management interface at `http://homeassistant-ip:8112`
2. Find the ZIM file you want to delete in the list
3. Click the "Delete" button
4. Confirm the deletion
5. The file will be removed and Kiwix will automatically update

## Accessing Kiwix Content

### Via Home Assistant Ingress (Recommended)

**✅ Fully Functional**: The add-on uses nginx reverse proxy with path rewriting to ensure all features work correctly via ingress.

1. Open Home Assistant
2. Click on "Kiwix" in the sidebar
3. You'll see a tabbed interface:
   - **Kiwix Wiki tab**: Browse and search ZIM files
   - **Management tab**: Download, upload, and manage ZIM files
4. All features work correctly:
   - ✅ Full CSS styling
   - ✅ Working JavaScript
   - ✅ Complete ZIM file list
   - ✅ Functional category and language selectors

### Via Direct Network Access

**Single Port Access:**
- **Landing Page**: `http://homeassistant-ip:8111/` - Tabbed interface (same as ingress)
- **Kiwix Wiki**: `http://homeassistant-ip:8111/wiki/` - Direct Kiwix access
- **Management**: `http://homeassistant-ip:8111/manage/` - File management

**To find your Home Assistant IP address:**
- Check your router's device list
- Or use `http://homeassistant.local:8111` if mDNS is enabled
- Or check Home Assistant Settings → System → Network

All features work identically via ingress or direct network access.

### Using ZIM Files

Once ZIM files are added:

1. Kiwix automatically detects new ZIM files (using `--monitorLibrary`)
2. No restart is needed when adding or removing files
3. Browse available content through the Kiwix interface
4. Search and read content offline

## Popular ZIM Files

### Wikipedia

- **Wikipedia (English, All)**: Complete English Wikipedia
  - URL: `https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_2023-01.zim`
  - Size: ~100GB (very large)

- **Wikipedia (English, Top 100)**: Top 100 English Wikipedia articles
  - URL: `https://download.kiwix.org/zim/wikipedia/wikipedia_en_top_100_maxi_2023-01.zim`
  - Size: ~500MB

### Other Content

- **Wiktionary**: Dictionary definitions
- **Project Gutenberg**: Free books
- **OpenStreetMap**: Map data
- **Vikidia**: Encyclopedia for children

Visit [kiwix.org](https://www.kiwix.org/en/downloads/) for a complete list.

## Network Configuration

### Ports

The add-on uses two ports:

- **8111/tcp**: Kiwix server (content serving)
- **8112/tcp**: Management API (file management)

Both ports are exposed and can be accessed from your local network.

### Firewall Configuration

If you want external access:

1. **Allow inbound TCP traffic** on port 8111 (Kiwix server)
2. **Allow inbound TCP traffic** on port 8112 (Management interface, optional)

### Router Configuration

For external access, configure port forwarding:

- Forward external port → 8111 (Kiwix server)
- Forward external port → 8112 (Management, optional)

## Troubleshooting

### Common Issues

**1. Kiwix server not starting**
- Check that port 8111 is not in use by another service
- Verify ZIM storage path is writable
- Check add-on logs for error messages

**2. Management interface not accessible**
- Check that port 8112 is not in use
- Verify `enable_management` is set to `true`
- Check add-on logs for management API errors
- **IMPORTANT**: Ensure port 8112 is enabled in the add-on's **Network** settings tab
  - Go to add-on → Network tab → Enable port 8112/tcp
- Verify the port is exposed: `nc -zv homeassistant-ip 8112`

**3. ZIM files not appearing**
- Verify files are in the correct directory (check `zim_storage_path`)
- Ensure files have `.zim` extension
- Check file permissions (should be readable)
- Kiwix uses `--monitorLibrary` to auto-detect files, but may take a few seconds

**4. Download fails**
- Check internet connectivity
- Verify URL is accessible
- Check available disk space
- Large files may take a long time to download

**5. Upload fails**
- Check file size doesn't exceed `max_upload_size`
- Verify file has `.zim` extension
- Check available disk space
- Ensure file is a valid ZIM file

### Logs

Enable debug logging for detailed information:

```yaml
log_level: "debug"
```

View logs in the Home Assistant add-on logs section.

### Checking ZIM Files

To manually check ZIM files:

1. Access the management interface
2. View the list of ZIM files
3. Check file sizes and dates
4. Verify files are valid ZIM format

## Performance Optimization

### Storage

- **Disk Space**: ZIM files can be very large (10-100GB+ for full Wikipedia)
- **Storage Location**: Ensure `zim_storage_path` has sufficient space
- **SSD Recommended**: For better performance, use SSD storage

### Network

- **Bandwidth**: Large ZIM files take significant time to download
- **Local Network**: For faster transfers, download on a local machine and upload
- **Multiple Files**: Kiwix can serve multiple ZIM files efficiently

### Resource Usage

- **CPU**: Low CPU usage, mainly for serving content
- **Memory**: Approximately 50-200MB base, plus caching
- **Disk I/O**: Moderate I/O when serving content

## Security Considerations

### Network Security

- **Local Network Only**: By default, accessible only on local network
- **External Access**: If exposing externally, consider firewall rules
- **Management Interface**: The management interface (port 8112) should ideally be restricted to local network

### File Security

- **ZIM Files**: ZIM files are read-only, safe to serve
- **Uploads**: Validate uploaded files are actual ZIM files
- **Storage**: Ensure storage directory has proper permissions

### Recommendations

- Keep management interface on local network only
- Use firewall rules to restrict access if needed
- Regularly update the add-on for security patches

## Advanced Configuration

### Custom Storage Path

For custom storage locations:

```yaml
zim_storage_path: "/share/kiwix/zim"
```

Ensure the path exists and is writable.

### Disabling Management Interface

To disable the management interface:

```yaml
enable_management: false
```

You'll need to manually add ZIM files via SSH or other methods.

### Large File Uploads

For very large ZIM files:

```yaml
max_upload_size: 50000  # 50GB
```

Note: Large uploads may take significant time and bandwidth.

## API Endpoints

The management API provides REST endpoints:

- `GET /api/zim` - List all ZIM files
- `POST /api/zim/download` - Download ZIM from URL
- `POST /api/zim/upload` - Upload ZIM file
- `DELETE /api/zim/{filename}` - Delete ZIM file
- `GET /api/zim/{filename}/info` - Get ZIM file info
- `GET /api/download/{job_id}/status` - Get download progress

## License

MIT License - see LICENSE file for details.

