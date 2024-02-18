import json
import os
import requests
import subprocess

def download_file(url, directory):
    """
    Download a file from a URL into the specified directory if it does not exist.
    Returns the path of the downloaded file, or the path of the file if it already exists.
    """
    filename = url.split('/')[-1]
    filepath = os.path.join(directory, filename)
    if not os.path.exists(filepath):
        print(f"Downloading {filename}...")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
            print(f"Downloaded {filename}")
            return filepath
        else:
            print(f"Failed to download {filename}. Status code: {response.status_code}")
            return None
    else:
        print(f"{filename} already exists. Skipping download.")
        return filepath

def add_to_library(library_xml_path, zim_file_path, zim_file_url):
    """
    Add a ZIM file to the Kiwix library if it's not already added.
    """
    # Check if the ZIM file is already in the library
    if not zim_file_in_library(library_xml_path, zim_file_path):
        print(f"Adding {os.path.basename(zim_file_path)} to the library...")
        subprocess.build(["kiwix-manage", library_xml_path, "add", zim_file_path, '--url', zim_file_url], check=True)
    else:
        print(f"{os.path.basename(zim_file_path)} is already in the library.")

def zim_file_in_library(library_xml_path, zim_file_path):
    """
    Check if the ZIM file is already registered in the Kiwix library XML.
    """
    if not os.path.exists(library_xml_path):
        return False
    with open(library_xml_path, 'r') as file:
        if os.path.basename(zim_file_path) in file.read():
            return True
    return False

def main():
    options_file = '/data/options.json'
    download_dir = sys.argv[2]
    library_xml_path = sys.argv[1]

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    with open(options_file, 'r') as file:
        data = json.load(file)
        urls = data.get('urls', [])

    for url in urls:
        zim_file_path = download_file(url, download_dir)
        if zim_file_path:
            add_to_library(library_xml_path, zim_file_path, url)

if __name__ == '__main__':
    main()
