import os
import rasterio
from rasterio.merge import merge
from rasterio.plot import show
from tqdm import tqdm

def merge_rasters(src_dir, output_path, batch_size=10):
    # List to store the sources
    src_files_to_mosaic = []

    # Iterate through all the .bil files in the directory
    for root, _, files in os.walk(src_dir):
        for file in tqdm(files, desc="Reading .bil files"):
            if file.endswith('.bil'):
                file_path = os.path.join(root, file)
                src = rasterio.open(file_path)
                src_files_to_mosaic.append(src)

                # Merge the rasters in batches
                if len(src_files_to_mosaic) >= batch_size:
                    mosaic, out_trans = merge(src_files_to_mosaic)

                    # Copy the metadata from the first raster
                    if len(src_files_to_mosaic) == batch_size:
                        out_meta = src.meta.copy()

                    # Write the mosaic raster to disk
                    with rasterio.open(output_path, "w", **out_meta) as dest:
                        dest.write(mosaic)

                    # Close all the open files
                    for src in src_files_to_mosaic:
                        src.close()

                    # Clear the list for the next batch
                    src_files_to_mosaic = []

    # Merge any remaining rasters
    if len(src_files_to_mosaic) > 0:
        mosaic, out_trans = merge(src_files_to_mosaic)

        # Write the mosaic raster to disk
        with rasterio.open(output_path, "w", **out_meta) as dest:
            dest.write(mosaic)

        # Close all the open files
        for src in src_files_to_mosaic:
            src.close()

    print(f"Composite image saved to {output_path}")

if __name__ == "__main__":
    src_dir = r"J:\GDA\GIS\LandsatEXTRACT"  # Directory containing the .bil files
    output_path = r"J:\GDA\GIS\LandsatDEM_composite_image.tif"  # Output path for the composite image

    merge_rasters(src_dir, output_path, batch_size=10)
