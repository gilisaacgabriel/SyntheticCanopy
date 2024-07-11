import zipfile
import os
import subprocess

def is_valid_zip(file_path):
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            corrupt = zip_ref.testzip()
            if corrupt is not None:
                print(f"Corrupt file found: {corrupt}")
                return False
            return True
    except zipfile.BadZipFile:
        print(f"Bad zip file: {file_path}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def validate_zip_files(directory):
    total_files = 0
    checked_files = 0
    invalid_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.zip'):
                total_files += 1

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.zip'):
                file_path = os.path.join(root, file)
                checked_files += 1
                print(f"Checking file: {file_path}")
                if not is_valid_zip(file_path):
                    print(f"Invalid zip file: {file_path}")
                    invalid_files.append(file_path)
                    os.remove(file_path)
                else:
                    print(f"Valid zip file: {file_path}")
                print(f"Progress: {checked_files}/{total_files} files checked")

    if invalid_files:
        print("Invalid files found. Running M2M-Download-API...")
        print("Invalid files:")
        for file in invalid_files:
            print(file)
        run_download_script()

def run_download_script():
    try:
        subprocess.run(['python', 'M2M-Download-API'], check=True)
        print("M2M-Download-API.py executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running M2M-Download-API: {e}")

if __name__ == "__main__":
    directory_to_check = r"J:\GDA\GIS\LandsatDOWNLOAD"  # Change this to the directory containing your zip files
    validate_zip_files(directory_to_check)