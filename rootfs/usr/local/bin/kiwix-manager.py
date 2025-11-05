#!/usr/bin/env python3
"""
Kiwix Management API
Provides REST API and web interface for managing ZIM files
"""

import os
import sys
import json
import argparse
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse
import threading
import time

import aiofiles
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Global state
app = FastAPI(title="Kiwix Management API")
download_jobs: Dict[str, Dict] = {}
storage_path: Path = None
max_upload_size: int = 10000 * 1024 * 1024  # Default 10GB in bytes

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_file_size(filepath: Path) -> int:
    """Get file size in bytes."""
    try:
        return filepath.stat().st_size
    except OSError:
        return 0


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def get_zim_info(filepath: Path) -> Dict:
    """Get ZIM file information."""
    try:
        stat = filepath.stat()
        return {
            "name": filepath.name,
            "size": stat.st_size,
            "size_formatted": format_size(stat.st_size),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        }
    except OSError as e:
        logger.error(f"Error getting file info for {filepath}: {e}")
        return None


def download_file_with_progress(url: str, filepath: Path, job_id: str):
    """Download file with progress tracking."""
    import urllib.request
    import urllib.error
    
    try:
        logger.info(f"Starting download: {url} -> {filepath}")
        download_jobs[job_id]["status"] = "downloading"
        download_jobs[job_id]["progress"] = 0
        
        def report_progress(block_num, block_size, total_size):
            if total_size > 0:
                downloaded = block_num * block_size
                progress = min(int((downloaded / total_size) * 100), 100)
                download_jobs[job_id]["progress"] = progress
                download_jobs[job_id]["downloaded"] = downloaded
                download_jobs[job_id]["total_size"] = total_size
                logger.info(f"Download progress: {progress}% ({format_size(downloaded)}/{format_size(total_size)})")
        
        urllib.request.urlretrieve(url, filepath, reporthook=report_progress)
        
        # Verify file was downloaded
        if filepath.exists() and filepath.stat().st_size > 0:
            download_jobs[job_id]["status"] = "completed"
            download_jobs[job_id]["progress"] = 100
            download_jobs[job_id]["file_size"] = filepath.stat().st_size
            logger.info(f"Download completed: {filepath.name} ({format_size(filepath.stat().st_size)})")
        else:
            download_jobs[job_id]["status"] = "failed"
            download_jobs[job_id]["error"] = "Downloaded file is empty or doesn't exist"
            logger.error(f"Download failed: file is empty")
            
    except Exception as e:
        download_jobs[job_id]["status"] = "failed"
        download_jobs[job_id]["error"] = str(e)
        logger.error(f"Download error: {e}")
        if filepath.exists():
            filepath.unlink()


@app.get("/", response_class=HTMLResponse)
async def management_ui():
    """Serve the management UI."""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kiwix ZIM File Manager</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 30px;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 30px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #34495e;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
        }
        input[type="text"], input[type="file"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, input[type="file"]:focus {
            outline: none;
            border-color: #3498db;
        }
        button {
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: background 0.3s;
        }
        button:hover {
            background: #2980b9;
        }
        button.delete {
            background: #e74c3c;
        }
        button.delete:hover {
            background: #c0392b;
        }
        .file-list {
            display: grid;
            gap: 15px;
        }
        .file-item {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .file-info {
            flex: 1;
        }
        .file-name {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
            font-size: 16px;
        }
        .file-meta {
            color: #7f8c8d;
            font-size: 14px;
        }
        .file-actions {
            display: flex;
            gap: 10px;
        }
        .progress-container {
            margin-top: 10px;
            display: none;
        }
        .progress-container.active {
            display: block;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 5px;
        }
        .progress-fill {
            height: 100%;
            background: #3498db;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: 600;
        }
        .status {
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 20px;
            display: none;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .status.active {
            display: block;
        }
        .upload-progress {
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Kiwix ZIM File Manager</h1>
        
        <div id="status" class="status"></div>
        
        <div class="section">
            <h2>Download ZIM File from URL</h2>
            <form id="downloadForm">
                <div class="form-group">
                    <label for="downloadUrl">ZIM File URL:</label>
                    <input type="text" id="downloadUrl" name="url" placeholder="https://download.kiwix.org/zim/wikipedia_en_all_2023-01.zim" required>
                </div>
                <button type="submit">Download</button>
                <div id="downloadProgress" class="progress-container">
                    <div class="progress-bar">
                        <div id="downloadProgressFill" class="progress-fill" style="width: 0%">0%</div>
                    </div>
                </div>
            </form>
        </div>
        
        <div class="section">
            <h2>Upload ZIM File</h2>
            <form id="uploadForm">
                <div class="form-group">
                    <label for="uploadFile">Select ZIM file:</label>
                    <input type="file" id="uploadFile" name="file" accept=".zim" required>
                </div>
                <button type="submit">Upload</button>
                <div id="uploadProgress" class="progress-container">
                    <div class="progress-bar">
                        <div id="uploadProgressFill" class="progress-fill" style="width: 0%">0%</div>
                    </div>
                </div>
            </form>
        </div>
        
        <div class="section">
            <h2>ZIM Files</h2>
            <div id="fileList" class="file-list">
                <p>Loading...</p>
            </div>
        </div>
    </div>
    
    <script>
        let downloadJobId = null;
        let downloadInterval = null;
        
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = `status ${type} active`;
            setTimeout(() => {
                status.classList.remove('active');
            }, 5000);
        }
        
        async function loadFiles() {
            try {
                const response = await fetch('/api/zim');
                const files = await response.json();
                const fileList = document.getElementById('fileList');
                
                if (files.length === 0) {
                    fileList.innerHTML = '<p style="color: #7f8c8d;">No ZIM files found. Upload or download files to get started.</p>';
                    return;
                }
                
                fileList.innerHTML = files.map(file => `
                    <div class="file-item">
                        <div class="file-info">
                            <div class="file-name">${file.name}</div>
                            <div class="file-meta">
                                Size: ${file.size_formatted} | 
                                Modified: ${new Date(file.modified).toLocaleString()}
                            </div>
                        </div>
                        <div class="file-actions">
                            <button class="delete" onclick="deleteFile('${file.name}')">Delete</button>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Error loading files:', error);
                showStatus('Error loading files: ' + error.message, 'error');
            }
        }
        
        async function deleteFile(filename) {
            if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
                return;
            }
            
            try {
                const response = await fetch(`/api/zim/${encodeURIComponent(filename)}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    showStatus(`File "${filename}" deleted successfully.`, 'success');
                    loadFiles();
                } else {
                    const error = await response.json();
                    showStatus('Error deleting file: ' + error.detail, 'error');
                }
            } catch (error) {
                showStatus('Error deleting file: ' + error.message, 'error');
            }
        }
        
        document.getElementById('downloadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const url = document.getElementById('downloadUrl').value;
            const progressContainer = document.getElementById('downloadProgress');
            const progressFill = document.getElementById('downloadProgressFill');
            
            progressContainer.classList.add('active');
            progressFill.style.width = '0%';
            progressFill.textContent = 'Starting...';
            
            try {
                const response = await fetch('/api/zim/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                
                const result = await response.json();
                if (response.ok) {
                    downloadJobId = result.job_id;
                    showStatus('Download started. Progress will be shown below.', 'success');
                    
                    // Poll for progress
                    downloadInterval = setInterval(async () => {
                        try {
                            const statusResponse = await fetch(`/api/download/${downloadJobId}/status`);
                            const status = await statusResponse.json();
                            
                            progressFill.style.width = status.progress + '%';
                            progressFill.textContent = status.progress + '%';
                            
                            if (status.status === 'completed') {
                                clearInterval(downloadInterval);
                                showStatus('Download completed successfully!', 'success');
                                progressContainer.classList.remove('active');
                                document.getElementById('downloadUrl').value = '';
                                loadFiles();
                            } else if (status.status === 'failed') {
                                clearInterval(downloadInterval);
                                showStatus('Download failed: ' + status.error, 'error');
                                progressContainer.classList.remove('active');
                            }
                        } catch (error) {
                            console.error('Error checking download status:', error);
                        }
                    }, 1000);
                } else {
                    showStatus('Error starting download: ' + result.detail, 'error');
                    progressContainer.classList.remove('active');
                }
            } catch (error) {
                showStatus('Error: ' + error.message, 'error');
                progressContainer.classList.remove('active');
            }
        });
        
        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById('uploadFile');
            const file = fileInput.files[0];
            
            if (!file) {
                showStatus('Please select a file to upload.', 'error');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            const progressContainer = document.getElementById('uploadProgress');
            const progressFill = document.getElementById('uploadProgressFill');
            progressContainer.classList.add('active');
            progressFill.style.width = '0%';
            progressFill.textContent = 'Uploading...';
            
            try {
                const xhr = new XMLHttpRequest();
                
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        progressFill.style.width = percentComplete + '%';
                        progressFill.textContent = Math.round(percentComplete) + '%';
                    }
                });
                
                xhr.addEventListener('load', () => {
                    if (xhr.status === 200) {
                        showStatus('File uploaded successfully!', 'success');
                        progressContainer.classList.remove('active');
                        fileInput.value = '';
                        loadFiles();
                    } else {
                        const error = JSON.parse(xhr.responseText);
                        showStatus('Upload failed: ' + error.detail, 'error');
                        progressContainer.classList.remove('active');
                    }
                });
                
                xhr.addEventListener('error', () => {
                    showStatus('Upload error occurred.', 'error');
                    progressContainer.classList.remove('active');
                });
                
                xhr.open('POST', '/api/zim/upload');
                xhr.send(formData);
            } catch (error) {
                showStatus('Error: ' + error.message, 'error');
                progressContainer.classList.remove('active');
            }
        });
        
        // Load files on page load
        loadFiles();
        
        // Refresh file list every 30 seconds
        setInterval(loadFiles, 30000);
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/zim")
async def list_zim_files():
    """List all ZIM files."""
    if storage_path is None or not storage_path.exists():
        return JSONResponse(content=[])
    
    zim_files = []
    for filepath in storage_path.glob("*.zim"):
        info = get_zim_info(filepath)
        if info:
            zim_files.append(info)
    
    # Sort by modified date (newest first)
    zim_files.sort(key=lambda x: x["modified"], reverse=True)
    return JSONResponse(content=zim_files)


@app.post("/api/zim/download")
async def download_zim_file(data: dict, background_tasks: BackgroundTasks):
    """Start downloading a ZIM file from URL."""
    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    # Validate URL
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    # Generate job ID
    job_id = f"download_{int(time.time())}"
    
    # Extract filename from URL
    filename = os.path.basename(parsed.path) or f"download_{int(time.time())}.zim"
    filepath = storage_path / filename
    
    # Check if file already exists
    if filepath.exists():
        raise HTTPException(status_code=400, detail=f"File {filename} already exists")
    
    # Initialize download job
    download_jobs[job_id] = {
        "job_id": job_id,
        "url": url,
        "filename": filename,
        "status": "pending",
        "progress": 0,
        "downloaded": 0,
        "total_size": 0,
        "started_at": datetime.now().isoformat(),
    }
    
    # Start download in background thread
    def download_task():
        download_file_with_progress(url, filepath, job_id)
    
    thread = threading.Thread(target=download_task, daemon=True)
    thread.start()
    
    logger.info(f"Started download job {job_id} for {url}")
    return JSONResponse(content={"job_id": job_id, "filename": filename, "status": "started"})


@app.get("/api/download/{job_id}/status")
async def get_download_status(job_id: str):
    """Get download job status."""
    if job_id not in download_jobs:
        raise HTTPException(status_code=404, detail="Download job not found")
    
    job = download_jobs[job_id]
    return JSONResponse(content={
        "job_id": job_id,
        "status": job["status"],
        "progress": job.get("progress", 0),
        "downloaded": job.get("downloaded", 0),
        "total_size": job.get("total_size", 0),
        "error": job.get("error"),
    })


@app.post("/api/zim/upload")
async def upload_zim_file(file: UploadFile = File(...)):
    """Upload a ZIM file."""
    if not file.filename.endswith('.zim'):
        raise HTTPException(status_code=400, detail="File must have .zim extension")
    
    filepath = storage_path / file.filename
    
    # Check if file already exists
    if filepath.exists():
        raise HTTPException(status_code=400, detail=f"File {file.filename} already exists")
    
    try:
        # Check file size during upload
        total_size = 0
        async with aiofiles.open(filepath, 'wb') as f:
            while chunk := await file.read(8192):
                total_size += len(chunk)
                if total_size > max_upload_size:
                    filepath.unlink(missing_ok=True)
                    raise HTTPException(status_code=413, detail=f"File size exceeds maximum allowed size ({format_size(max_upload_size)})")
                await f.write(chunk)
        
        # Verify file was written
        if not filepath.exists() or filepath.stat().st_size == 0:
            raise HTTPException(status_code=500, detail="Upload failed: file is empty")
        
        logger.info(f"Uploaded file: {file.filename} ({format_size(filepath.stat().st_size)})")
        return JSONResponse(content={
            "filename": file.filename,
            "size": filepath.stat().st_size,
            "size_formatted": format_size(filepath.stat().st_size),
        })
    except HTTPException:
        raise
    except Exception as e:
        filepath.unlink(missing_ok=True)
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.delete("/api/zim/{filename}")
async def delete_zim_file(filename: str):
    """Delete a ZIM file."""
    # Security: prevent directory traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    filepath = storage_path / filename
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        filepath.unlink()
        logger.info(f"Deleted file: {filename}")
        return JSONResponse(content={"message": f"File {filename} deleted successfully"})
    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


@app.get("/api/zim/{filename}/info")
async def get_zim_file_info(filename: str):
    """Get information about a specific ZIM file."""
    # Security: prevent directory traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    filepath = storage_path / filename
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    info = get_zim_info(filepath)
    if not info:
        raise HTTPException(status_code=500, detail="Failed to get file information")
    
    return JSONResponse(content=info)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Kiwix Management API")
    parser.add_argument("--port", type=int, default=8112, help="Port to listen on")
    parser.add_argument("--storage-path", type=str, required=True, help="Path to ZIM storage directory")
    parser.add_argument("--max-upload-size", type=int, default=10000, help="Maximum upload size in MB")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    
    args = parser.parse_args()
    
    global storage_path, max_upload_size
    storage_path = Path(args.storage_path)
    max_upload_size = args.max_upload_size * 1024 * 1024  # Convert MB to bytes
    
    # Ensure storage path exists
    storage_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Starting Kiwix Management API on {args.host}:{args.port}")
    logger.info(f"ZIM storage path: {storage_path}")
    logger.info(f"Max upload size: {format_size(max_upload_size)}")
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    main()

