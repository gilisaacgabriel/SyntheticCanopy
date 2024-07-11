""" 
This script extracts all the zip files from downloaded Landsat C2 DEM folder into a new folder.
1. It checks if the file has already been extracted. This was necessary because some files were broken and had to be deleted, redownloaded, and extracted.
2. It prints and logs each file that is being extracted.

Make sure to change the source_directory and destination_directory to your source and destination folders. 

"""
import zipfile
import os
from tqdm import tqdm

def get_zip_contents(zip_file_path):
    """
    Get the list of files in a zip file.
    """
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        return set(zip_ref.namelist())

def get_extracted_contents(extract_to_path):
    """
    Get the list of files in the extracted directory.
    """
    extracted_files = set()
    for root, _, files in os.walk(extract_to_path):
        for file in files:
            # Get the relative path of the file with respect to the extraction directory
            relative_path = os .path.relpath(os.path.join(root, file), extract_to_path)
            extracted_files.add(relative_path)
    return extracted_files

def is_already_extracted(zip_file_path, extract_to_path):
    """
    Check if the zip file contents already exist in the extraction directory.
    """
    zip_contents = get_zip_contents(zip_file_path)
    extracted_contents = get_extracted_contents(extract_to_path)
    return zip_contents.issubset(extracted_contents)

def extract_zip(zip_file_path, extract_to_path):
    """
    Extract a zip file to the specified directory.
    """
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to_path)

def extract_zip_files(source_directory, extract_to_path):
    """
    Extract all zip files in the source directory to the specified directory.
    Only extract if the contents are not already present.
    """
    zip_files = [os.path.join(root, file) for root, _, files in os.walk(source_directory) for file in files if file.endswith('.zip')]
    
    for zip_file_path in tqdm(zip_files, desc="Processing ZIP files"):
        if not is_already_extracted(zip_file_path, extract_to_path):
            print(f"\nExtracting {zip_file_path} to {extract_to_path}")
            extract_zip(zip_file_path, extract_to_path)
        else:
            print(f"\n{zip_file_path} has already been extracted.")

if __name__ == "__main__":
    source_directory = r"J:\GDA\GIS\LandsatDOWNLOAD"  # Change this to your source directory containing zip files
    extract_to_path = r"J:\GDA\GIS\LandsatEXTRACT"  # Change this to your desired extraction directory

    # Ensure the extract_to_path exists
    os.makedirs(extract_to_path, exist_ok=True)

    extract_zip_files(source_directory, extract_to_path)
