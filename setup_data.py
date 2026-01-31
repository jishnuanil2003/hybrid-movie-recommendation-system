import os
import requests
import zipfile
import io

def download_and_extract_data():
    url = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
    print(f"Downloading data from {url}...")
    
    response = requests.get(url)
    if response.status_code == 200:
        print("Download complete. Extracting...")
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Extract all to the 'data' directory
            z.extractall("data")
            
        # Move files from subdirectory to main data folder for easier access
        source_dir = "data/ml-latest-small"
        target_dir = "data"
        
        if os.path.exists(source_dir):
            for filename in os.listdir(source_dir):
                old_path = os.path.join(source_dir, filename)
                new_path = os.path.join(target_dir, filename)
                os.rename(old_path, new_path)
            os.rmdir(source_dir)
            
        print("Data setup complete. Files are in 'data/' directory.")
        print("Files:", os.listdir(target_dir))
    else:
        print(f"Failed to download data. Status code: {response.status_code}")

if __name__ == "__main__":
    download_and_extract_data()
