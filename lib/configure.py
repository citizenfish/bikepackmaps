import json
import requests
import os
import zipfile


def download_and_extract(data):
    for item in data:
        url = item.get('url')
        download_location = item.get('download_location')
        if not clear_directory(download_location):
            continue

        file_type = item.get('type', 'zip')
        filename = item.get('filename', f'download.{file_type}')
        d_filename = f'{download_location}/{filename}'
        # Download the file
        print(f"Downloading {url} to {download_location}/{filename}")

        response = requests.get(url, stream=True)
        with open(d_filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        # Check if type is 'unzip' and unzip it
        if file_type == 'unzip':
            print(f"Unzipping {d_filename}...")
            with zipfile.ZipFile(d_filename, 'r') as zip_ref:
                extract_folder = download_location
                os.makedirs(extract_folder, exist_ok=True)
                zip_ref.extractall(extract_folder)


def clear_directory(directory_path):
    # Check if directory exists
    if not os.path.isdir(directory_path):
        print(f"'{directory_path}' is not a valid directory!")
        return False

    # List all files and sub-directories in the given directory
    contents = os.listdir(directory_path)

    # If the directory is empty
    if not contents:
        print(f"The directory '{directory_path}' is empty, downloading....")
        return True

    # Ask user if they want to delete all files and sub-directories
    choice = input(f"The directory '{directory_path}' is not empty. Do you want to delete all its contents and download? (yes/no): ").strip().lower()

    if choice[0].lower() == 'y':
        for item in contents:
            item_path = os.path.join(directory_path, item)

            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                os.rmdir(item_path)  # Note: This will only remove empty directories

        print(f"All contents of '{directory_path}' have been deleted.")
        return True
    else:
        return False

# Example usage
# directory_path = "path_to_some_directory"
# clear_directory(directory_path)

if __name__ == '__main__':
    # Read the config.json file
    with open('config.json', 'r') as file:
        data = json.load(file)

    # Check if data is a list of dictionaries
    downloads = data.get('downloads')

    if downloads:
        download_and_extract(downloads)
