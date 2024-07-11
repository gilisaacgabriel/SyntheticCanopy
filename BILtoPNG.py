import os
import glob
from osgeo import gdal
from osgeo import osr
import numpy as np
from PIL import Image

def convert_bil_to_png(bil_file, output_directory):
    try:
        # Open the .bil file
        dataset = gdal.Open(bil_file)
        if not dataset:
            print(f"Failed to open {bil_file}")
            return False

        # Read the data
        band = dataset.GetRasterBand(1)
        data = band.ReadAsArray()

        # Normalize data to 16-bit range
        data = ((data - np.min(data)) / (np.max(data) - np.min(data)) * 65535).astype(np.uint16)

        # Create a new image
        png_file = os.path.join(output_directory, os.path.basename(bil_file).replace('.bil', '.png'))
        image = Image.fromarray(data)
        image.save(png_file, 'PNG')

        # Copy geospatial information and metadata
        src_proj = dataset.GetProjection()
        src_geotrans = dataset.GetGeoTransform()
        
        dst_dataset = gdal.GetDriverByName('PNG').Create(png_file, dataset.RasterXSize, dataset.RasterYSize, 1, gdal.GDT_UInt16)
        dst_dataset.GetRasterBand(1).WriteArray(data)
        dst_dataset.SetGeoTransform(src_geotrans)
        dst_dataset.SetProjection(src_proj)

        # Close datasets
        dst_dataset = None
        dataset = None

        print(f"Successfully converted {bil_file} to {png_file}")
        return True
    except Exception as e:
        print(f"An error occurred while converting {bil_file}: {e}")
        return False

def process_all_bil_files(source_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    bil_files = glob.glob(os.path.join(source_directory, '*.bil'))
    total_files = len(bil_files)

    print(f"Found {total_files} .bil files to process.")

    for index, bil_file in enumerate(bil_files):
        print(f"Processing file {index + 1}/{total_files}: {bil_file}")
        convert_bil_to_png(bil_file, output_directory)

if __name__ == "__main__":
    source_directory = r"K:\GDA\GIS\LandsatEXTRACT"  # Change this to your source folder
    output_directory = r"K:\GDA\GIS\LandsatEXTRACTPNG"  # Change this to your output folder
    process_all_bil_files(source_directory, output_directory)