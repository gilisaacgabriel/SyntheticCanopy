import os
import OpenEXR
import Imath
import numpy as np
import tifffile as tiff

def exr_to_tif(exr_path, tif_path):
    print(f"Processing file: {exr_path}")
    try:
        # Open the EXR file
        exr_file = OpenEXR.InputFile(exr_path)
        print("File opened successfully.")

        # Get the data window of the EXR file
        data_window = exr_file.header()['dataWindow']
        width = data_window.max.x - data_window.min.x + 1
        height = data_window.max.y - data_window.min.y + 1
        print(f"Image dimensions: width={width}, height={height}")

        # Define the channels for both RGB and DSM images
        channels = ['R', 'G', 'B']

        # Read the pixel data for each channel
        pt = Imath.PixelType(Imath.PixelType.FLOAT)
        channel_data = [np.frombuffer(exr_file.channel(c, pt), dtype=np.float32) for c in channels]
        channel_data = [c.reshape((height, width)) for c in channel_data]

        # Stack the channels
        image_data = np.stack(channel_data, axis=-1)
        print("Channels processed.")

        # Convert the image data to uint16 for TIF format
        image_data_uint16 = (image_data * 65535).astype(np.uint16)

        # Save the image data using tifffile
        tiff.imwrite(tif_path, image_data_uint16, photometric='rgb')
        print(f"Image saved to {tif_path}")
    except Exception as e:
        print(f"Error processing file {exr_path}: {e}")

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
                exr_to_tif(file_path, output_path)
            elif "AbsoluteZPosition-DEPTH" in file_name:
                output_name = f"{base_name}_DSM.tif"
                output_path = os.path.join(output_folder_dsm, output_name)
                print(f"Detected DSM file: {file_name}")
                exr_to_tif(file_path, output_path)
    print("Batch processing completed.")

# Example usage
input_folder = r'I:\GDA\UnrealEngine\SyntheticCanopies\Saved\MovieRenders\Jul22\Orthographic3'
output_folder_rgb = r'D:\gabriel.245\OneDrive - The Ohio State University\Qin\Poster\Orthographic\RGB'
output_folder_dsm = r'D:\gabriel.245\OneDrive - The Ohio State University\Qin\Poster\Orthographic\DSM'

# Ensure output directories exist
os.makedirs(output_folder_rgb, exist_ok=True)
os.makedirs(output_folder_dsm, exist_ok=True)

batch_process_exr_files(input_folder, output_folder_rgb, output_folder_dsm)
