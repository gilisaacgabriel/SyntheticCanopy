import os
import shutil

def move_contents(source_directory, destination_directory):
    # Ensure the destination directory exists
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
    
    for root, dirs, files in os.walk(source_directory):
        # Create corresponding directories in the destination
        for dir_name in dirs:
            source_dir = os.path.join(root, dir_name)
            relative_path = os.path.relpath(source_dir, source_directory)
            dest_dir = os.path.join(destination_directory, relative_path)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
        
        # Move files to the destination
        for file_name in files:
            source_file = os.path.join(root, file_name)
            relative_path = os.path.relpath(source_file, source_directory)
            dest_file = os.path.join(destination_directory, relative_path)
            print(f"Moving {source_file} to {dest_file}")
            shutil.move(source_file, dest_file)
    
    # Remove empty directories in the source directory
    for root, dirs, _ in os.walk(source_directory, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                print(f"Removed empty directory {dir_path}")

if __name__ == "__main__":
    source_directory = r"C:\Landsat-OneTenthDegSqs"  # Source directory
    destination_directory = r"I:\Landsat-OneTenthDegSqs"  # Destination directory
    move_contents(source_directory, destination_directory)
