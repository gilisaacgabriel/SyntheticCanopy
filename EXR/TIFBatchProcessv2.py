import os
import OpenEXR
import Imath
import numpy as np
import imageio

def exr_to_tif_dsm(exr_path, tif_path):
    print(f"Processing DSM file: {exr_path}")
    try:
        # Open the EXR file
        exr_file = OpenEXR.InputFile(exr_path)

        # Get the data window of the EXR file
        data_window = exr_file.header()['dataWindow']
        width = data_window.max.x - data_window.min.x + 1
        height = data_window.max.y - data_window.min.y + 1

        # Define the channels (assuming depth is stored in RGB channels)
        channels = ['R', 'G', 'B']
        
        # Read the pixel data for each channel
        pt = Imath.PixelType(Imath.PixelType.FLOAT)
        channel_data = [np.frombuffer(exr_file.channel(c, pt), dtype=np.float32) for c in channels]
        
        # Reshape the channel data to the image size
        channel_data = [c.reshape((height, width)) for c in channel_data]
        
        # Average the RGB channels to get the grayscale depth map
        depth_data = np.mean(np.stack(channel_data, axis=-1), axis=-1)
        
        # Normalize depth data for better visualization
        min_val = np.min(depth_data)
        max_val = np.max(depth_data)
        depth_data_normalized = (depth_data - min_val) / (max_val - min_val)
        
        # Convert the image data to uint16 for TIFF format
        depth_data_uint16 = (depth_data_normalized * 65535).astype(np.uint16)
        
        # Save the image as TIFF
        imageio.imwrite(tif_path, depth_data_uint16)
        print(f"Converted {exr_path} to {tif_path}")
    except Exception as e:
        print(f"Error processing DSM file {exr_path}: {e}")

def exr_to_tif_rgb(exr_path, tif_path):
    print(f"Processing RGB file: {exr_path}")
    try:
        # Open the EXR file
        exr_file = OpenEXR.InputFile(exr_path)

        # Get the data window of the EXR file
        data_window = exr_file.header()['dataWindow']
        width = data_window.max.x - data_window.min.x + 1
        height = data_window.max.y - data_window.min.y + 1

        # Define the channels for RGB images
        channels = ['R', 'G', 'B']

        # Read the pixel data for each channel
        pt = Imath.PixelType(Imath.PixelType.FLOAT)
        channel_data = [np.frombuffer(exr_file.channel(c, pt), dtype=np.float32) for c in channels]
        channel_data = [c.reshape((height, width)) for c in channel_data]

        # Stack the channels
        image_data = np.stack(channel_data, axis=-1)

        # Convert the image data to uint16 for TIFF format
        image_data_uint16 = (image_data * 65535).astype(np.uint16)

        # Save the image as TIFF
        imageio.imwrite(tif_path, image_data_uint16)
        print(f"Converted {exr_path} to {tif_path}")
    except Exception as e:
        print(f"Error processing RGB file {exr_path}: {e}")

def batch_process_exr_files(input_folder, output_folder_rgb, output_folder_dsm):
    print(f"Starting batch processing in folder: {input_folder}")
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".exr"):
            file_path = os.path.join(input_folder, file_name)
            base_name = file_name.split(' - ')[2].split('.')[0]
            if "PathTracer" in file_name and "AbsoluteZPosition-DEPTH" not in file_name:
                output_name = f"{base_name}_RGB.tif"
                output_path = os.path.join(output_folder_rgb, output_name)
                print(f"Detected RGB file: {file_name}")
                exr_to_tif_rgb(file_path, output_path)
            elif "AbsoluteZPosition-DEPTH" in file_name:
                output_name = f"{base_name}_DSM.tif"
                output_path = os.path.join(output_folder_dsm, output_name)
                print(f"Detected DSM file: {file_name}")
                exr_to_tif_dsm(file_path, output_path)
    print("Batch processing completed.")

# Example usage
input_folder = r'I:\GDA\UnrealEngine\SyntheticCanopies\Saved\MovieRenders\Jul22\56_350417__-69_350417-WINTER'
output_folder_rgb = r'K:\Dataset TIF\RGB'
output_folder_dsm = r'K:\Dataset TIF\DSM'

# Ensure output directories exist
os.makedirs(output_folder_rgb, exist_ok=True)
os.makedirs(output_folder_dsm, exist_ok=True)

batch_process_exr_files(input_folder, output_folder_rgb, output_folder_dsm)
