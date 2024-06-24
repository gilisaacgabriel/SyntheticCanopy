import os
import glob
from osgeo import gdal

def merge_images(source_directory, output_file):
    # Get list of all .bil files in the source directory
    file_list = glob.glob(os.path.join(source_directory, '*.bil'))
    
    if not file_list:
        print("No .bil files found in the source directory.")
        return
    
    # Create a VRT (Virtual Dataset) to merge all images
    vrt_options = gdal.BuildVRTOptions(resampleAlg='cubic', addAlpha=True)
    vrt = gdal.BuildVRT('/vsimem/temporary.vrt', file_list, options=vrt_options)
    
    if vrt is None:
        print("Failed to create VRT.")
        return

    # Translate the VRT to a final composite GeoTIFF
    print(f"Merging {len(file_list)} images into {output_file}...")
    gdal.Translate(output_file, vrt, format='GTiff')
    
    # Clean up the virtual dataset
    vrt = None
    print(f"Composite image saved as {output_file}")

if __name__ == "__main__":
    source_directory = './source_folder'  # Change this to your source folder containing DTM images
    output_file = './composite_image.tif'  # Change this to your desired output file path
    merge_images(source_directory, output_file)
