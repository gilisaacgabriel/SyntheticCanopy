import os
import gdal
import numpy as np
from PIL import Image

def geotiff_to_png(input_folder, output_folder):
    # Make sure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get list of GeoTIFF files in the input folder
    tiff_files = [f for f in os.listdir(input_folder) if f.endswith('.tif') or f.endswith('.tiff')]

    for tiff_file in tiff_files:
        # Open GeoTIFF file
        dataset = gdal.Open(os.path.join(input_folder, tiff_file))
        if dataset is None:
            print(f"Could not open {tiff_file}")
            continue

        # Read raster data
        band = dataset.GetRasterBand(1)
        raster = band.ReadAsArray()

        # Convert to uint16
        raster_uint16 = np.uint16(raster)

        # Create PNG image
        image = Image.fromarray(raster_uint16)

        # Save PNG file
        png_file = os.path.splitext(tiff_file)[0] + '.png'
        image.save(os.path.join(output_folder, png_file), format='PNG')

        print(f"Converted {tiff_file} to {png_file}")

    print("Conversion complete.")

# Specify input and output folders
input_folder = r"C:\Users\giegi\OneDrive - The Ohio State University\Qin\LandsatDEM-1kmsq"
output_folder = r"C:\Users\giegi\OneDrive - The Ohio State University\Qin\LandsatDEM-1kmsq\PNGs"

# Convert GeoTIFF files to PNG
geotiff_to_png(input_folder, output_folder)