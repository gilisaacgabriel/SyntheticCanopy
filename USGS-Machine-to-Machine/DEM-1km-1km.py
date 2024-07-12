""" 1. I have Approx 20,000 Digital Terrain Model images representing the world land cover in .bil format. Provide a script that divides each image into numerous 1km*1km squares in geotiff format, retaining geospatial information/metadata. I want each filename to be the coordinate of the center of the square in Decimal Degrees N/S and E/W. 
2. I would like this to be a verbose script showing me progress.
3. I have to stop the script every now and then. Please revise the script so that it can continue from where it was last instead of starting from the very beginning as there are many files.
4. the problem is that i have already processed many files without the checkpoint file."""
import os
from osgeo import gdal
import numpy as np
import json

CHECKPOINT_FILE = 'checkpoint.json'

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    return {'current_file': 0, 'current_square': 0}

def save_checkpoint(current_file, current_square):
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({'current_file': current_file, 'current_square': current_square}, f)

def bil_to_geotiff(source_directory, destination_directory, square_size_km=1):
    # Ensure destination directory exists
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
    
    checkpoint = load_checkpoint()
    current_file = checkpoint['current_file']
    current_square = checkpoint['current_square']

    all_files = [os.path.join(root, file)
                 for root, _, files in os.walk(source_directory)
                 for file in files if file.endswith('.bil')]

    total_files = len(all_files)

    for idx, file_path in enumerate(all_files[current_file:], start=current_file):
        print(f"Processing file {idx + 1}/{total_files}: {file_path}")
        process_bil_file(file_path, destination_directory, square_size_km, idx, current_square)
        current_square = 0  # Reset square count after each file
        current_file = idx + 1
        save_checkpoint(current_file, current_square)
        print(f"Finished processing {file_path}")

def process_bil_file(file_path, destination_directory, square_size_km, current_file_idx, start_square_idx):
    dataset = gdal.Open(file_path)
    if dataset is None:
        print(f"Failed to open {file_path}")
        return

    geotransform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()
    band = dataset.GetRasterBand(1)
    nodata = band.GetNoDataValue()
    data = band.ReadAsArray()

    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    pixel_width = geotransform[1]
    pixel_height = geotransform[5]
    square_size_deg = square_size_km / 111
    pixels_per_square_x = int(square_size_deg / pixel_width)
    pixels_per_square_y = int(abs(square_size_deg / pixel_height))
    total_squares = (cols // pixels_per_square_x) * (rows // pixels_per_square_y)
    current_square = start_square_idx

    for i in range(0, cols, pixels_per_square_x):
        for j in range(0, rows, pixels_per_square_y):
            if current_square < start_square_idx:
                current_square += 1
                continue

            min_lon = geotransform[0] + i * pixel_width
            max_lat = geotransform[3] + j * pixel_height
            center_lon = min_lon + (pixels_per_square_x * pixel_width) / 2
            center_lat = max_lat + (pixels_per_square_y * pixel_height) / 2

            filename = f"{center_lat:.6f}_{center_lon:.6f}.tif"
            output_path = os.path.join(destination_directory, filename)

            if os.path.exists(output_path):
                print(f"Skipping existing file: {output_path}")
                current_square += 1
                continue

            subset = data[j:j + pixels_per_square_y, i:i + pixels_per_square_x]
            if nodata is not None:
                subset[subset == nodata] = np.nan

            if subset.size == 0:
                continue

            driver = gdal.GetDriverByName('GTiff')
            out_raster = driver.Create(output_path, pixels_per_square_x, pixels_per_square_y, 1, gdal.GDT_Float32)
            out_raster.SetGeoTransform((min_lon, pixel_width, 0, max_lat, 0, pixel_height))
            out_raster.SetProjection(projection)
            outband = out_raster.GetRasterBand(1)
            outband.WriteArray(subset)
            if nodata is not None:
                outband.SetNoDataValue(nodata)

            outband.FlushCache()
            out_raster = None

            current_square += 1
            save_checkpoint(current_file_idx, current_square)
            print(f"Processed {current_square}/{total_squares} squares from {file_path}")

if __name__ == "__main__":
    source_directory = r"J:\GDA\GIS\LandsatEXTRACT"  # Change this to your source folder containing .bil files
    destination_directory = r"J:\GDA\GIS\LandsatDEM-1kmsq"  # Change this to your desired destination folder
    bil_to_geotiff(source_directory, destination_directory)
