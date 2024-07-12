import os
import gdal
import numpy as np
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

CHECKPOINT_FILE = 'checkpoint.json'
MAX_WORKERS = 4  # Adjust this based on your system's capabilities

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    return {'current_file': 0, 'current_tile': 0}

def save_checkpoint(current_file, current_tile):
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({'current_file': current_file, 'current_tile': current_tile}, f)

def bil_to_png(source_directory, destination_directory, tile_size_deg=0.1):
    # Ensure destination directory exists
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
    
    checkpoint = load_checkpoint()
    current_file = checkpoint['current_file']
    current_tile = checkpoint['current_tile']

    all_files = [os.path.join(root, file)
                 for root, _, files in os.walk(source_directory)
                 for file in files if file.endswith('.bil')]

    total_files = len(all_files)

    for idx, file_path in enumerate(all_files[current_file:], start=current_file):
        print(f"Processing file {idx + 1}/{total_files}: {file_path}")
        process_bil_file(file_path, destination_directory, tile_size_deg, idx, current_tile)
        current_tile = 0  # Reset tile count after each file
        current_file = idx + 1
        save_checkpoint(current_file, current_tile)
        print(f"Finished processing {file_path}")

def process_tile(subset, output_path, pgw_path, geotransform, nodata):
    # Convert the array to 16-bit unsigned integer
    subset = subset.astype(np.uint16)

    # Create and save the PNG file
    img = Image.fromarray(subset)
    img.save(output_path, format='PNG')

    # Create and save the world file (.pgw) for georeferencing
    with open(pgw_path, 'w') as f:
        f.write(f"{geotransform[1]:.10f}\n")
        f.write(f"{geotransform[2]:.10f}\n")
        f.write(f"{geotransform[4]:.10f}\n")
        f.write(f"{geotransform[5]:.10f}\n")
        f.write(f"{geotransform[0] + geotransform[1] / 2:.10f}\n")
        f.write(f"{geotransform[3] + geotransform[5] / 2:.10f}\n")

def process_bil_file(file_path, destination_directory, tile_size_deg, current_file_idx, start_tile_idx):
    dataset = gdal.Open(file_path)
    if dataset is None:
        print(f"Failed to open {file_path}")
        return

    geotransform = dataset.GetGeoTransform()
    band = dataset.GetRasterBand(1)
    nodata = band.GetNoDataValue()
    data = band.ReadAsArray()

    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    pixel_width = geotransform[1]
    pixel_height = geotransform[5]
    pixels_per_tile_x = int(tile_size_deg / pixel_width)
    pixels_per_tile_y = int(abs(tile_size_deg / pixel_height))
    total_tiles = (cols // pixels_per_tile_x) * (rows // pixels_per_tile_y)
    current_tile = start_tile_idx

    futures = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for i in range(0, cols, pixels_per_tile_x):
            for j in range(0, rows, pixels_per_tile_y):
                if current_tile < start_tile_idx:
                    current_tile += 1
                    continue

                min_lon = geotransform[0] + i * pixel_width
                max_lat = geotransform[3] + j * pixel_height
                center_lon = min_lon + (pixels_per_tile_x * pixel_width) / 2
                center_lat = max_lat + (pixels_per_tile_y * pixel_height) / 2

                filename = f"{center_lat:.6f}_{center_lon:.6f}.png"
                output_path = os.path.join(destination_directory, filename)
                pgw_path = os.path.splitext(output_path)[0] + '.pgw'

                if os.path.exists(output_path) and os.path.exists(pgw_path):
                    print(f"Skipping existing file: {output_path}")
                    current_tile += 1
                    continue

                subset = data[j:j + pixels_per_tile_y, i:i + pixels_per_tile_x]
                if nodata is not None:
                    subset[subset == nodata] = 0  # Optional: set NoData values to 0 or another value

                if subset.size == 0:
                    continue

                geotransform_subset = (min_lon, pixel_width, 0, max_lat, 0, pixel_height)
                futures.append(executor.submit(process_tile, subset, output_path, pgw_path, geotransform_subset, nodata))

                current_tile += 1

                if len(futures) >= MAX_WORKERS * 2:  # Limit number of queued futures to avoid memory issues
                    for future in as_completed(futures):
                        future.result()
                    futures = []

            save_checkpoint(current_file_idx, current_tile)
            print(f"Processed {current_tile}/{total_tiles} tiles from {file_path}")

        for future in as_completed(futures):
            future.result()

if __name__ == "__main__":
    source_directory = r"J:\GDA\GIS\LandsatEXTRACT"  # Change this to your source folder containing .bil files
    destination_directory = r"J:\GDA\GIS\Landsat-OneTenthDegSqs"  # Change this to your desired destination folder
    bil_to_png(source_directory, destination_directory)