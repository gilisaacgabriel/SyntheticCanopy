""" 
This script extracts all the zip files from downloaded Landsat C2 DEM folder into a new folder.
1. It checks if the file has already been extracted. This was necessary because some files were broken and had to be deleted, redownloaded, and extracted.
2. It prints and logs each file that is being extracted.

Make sure to change the source_directory and destination_directory to your source and destination folders. 

"""

import zipfile
import os
import logging

def unzip_files(directory, destination_directory):
    # Ensure destination directory exists
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
    
    # Set up logging
    logging.basicConfig(filename='unzip.log', level=logging.INFO)
    
    # Iterate over all files in the source directory
    for root, _, files in os.walk(source_directory):
        for file in files:
            if file.endswith('.zip'):
                file_path = os.path.join(root, file)
                extract_path = os.path.join(destination_directory, os.path.splitext(file)[0])
                
                # Check if the file has already been extracted
                if os.path.exists(extract_path):
                    print(f"Skipping {file_path} as it has already been extracted")
                    logging.info("Skipping %s as it has already been extracted", file_path)
                    continue
                
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        print(f"Unzipping {file_path} to {destination_directory}")
                        logging.info(f"Unzipping {file_path} to {destination_directory}")
                        zip_ref.extractall(destination_directory)
                        print(f"Successfully unzipped {file_path}")
                except zipfile.BadZipFile:
                    print(f"Bad zip file: {file_path}")
                    logging.error(f"Bad zip file: {file_path}")
                except Exception as e:
                    print(f"An error occurred with file {file_path}: {e}")
                    logging.error(f"An error occurred with file {file_path}: {e}")

if __name__ == "__main__":
    source_directory = r"K:\GDA\GIS\LandsatDOWNLOAD"  # Change this to your source folder
    destination_directory = r"K:\GDA\GIS\LandsatEXTRACT"  # Change this to your destination folder
    unzip_files(source_directory, destination_directory)
