import OpenEXR
import os

def inspect_exr_channels(exr_path):
    try:
        # Open the EXR file
        exr_file = OpenEXR.InputFile(exr_path)
        
        # Get the list of channels
        channels = exr_file.header()['channels'].keys()
        return channels
    except Exception as e:
        print(f"Error inspecting file {exr_path}: {e}")
        return []

def batch_inspect_exr_channels(input_folder):
    print(f"Inspecting EXR files in folder: {input_folder}")
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".exr"):
            file_path = os.path.join(input_folder, file_name)
            channels = inspect_exr_channels(file_path)
            print(f"File: {file_name}")
            print(f"Channels: {channels}")
            print()

# Example usage
input_folder = r'I:\GDA\UnrealEngine\SyntheticCanopies\Saved\MovieRenders\Jul22'
batch_inspect_exr_channels(input_folder)
