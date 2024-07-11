""" I have Approx 20,000 Digital Terrain Model images representing the world land cover in .bil format. Provide a script that divides each image into numerous 1km*1km squares in geotiff format, retaining geospatial information/metadata. I want each filename to be the coordinate of the center of the square in Decimal Degrees N/S and E/W. I would like this to be a verbose script showing me progress."""
import os
from osgeo import gdal
import numpy as np

def bil_to_geotiff(source_directory, destination_directory, square_size_km=1):
    # Ensure destination directory exists
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
    
    total_files = sum([len(files) for r, d, files in os.walk(source_directory)])
    current_file = 0

    for root, _, files in os.walk(source_directory):
        for file in files:
            if file.endswith('.bil'):
                current_file += 1
                print(f"Processing file {current_file}/{total_files}: {file}")
                file_path = os.path.join(root, file)
                process_bil_file(file_path, destination_directory, square_size_km)
                print(f"Finished processing {file}")

def process_bil_file(file_path, destination_directory, square_size_km):
    dataset = gdal.Open(file_path)
    if dataset is None:
        print(f"Failed to open {file_path}")
        return

    geotransform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()
    band = dataset.GetRasterBand(1)
    nodata = band.GetNoDataValue()
    data = band.ReadAsArray()

    # Get the number of columns and rows
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize

    # Get the pixel size in degrees
    pixel_width = geotransform[1]
    pixel_height = geotransform[5]

    # Convert square size from km to degrees
    square_size_deg = square_size_km / 111  # Approximation: 1 degree ~ 111 km

    # Calculate the number of pixels per square
    pixels_per_square_x = int(square_size_deg / pixel_width)
    pixels_per_square_y = int(abs(square_size_deg / pixel_height))

    total_squares = (cols // pixels_per_square_x) * (rows // pixels_per_square_y)
    current_square = 0

    for i in range(0, cols, pixels_per_square_x):
        for j in range(0, rows, pixels_per_square_y):
            subset = data[j:j + pixels_per_square_y, i:i + pixels_per_square_x]
            if nodata is not None:
                subset[subset == nodata] = np.nan

            if subset.size == 0:
                continue

            min_lon = geotransform[0] + i * pixel_width
            max_lat = geotransform[3] + j * pixel_height
            center_lon = min_lon + (pixels_per_square_x * pixel_width) / 2
            center_lat = max_lat + (pixels_per_square_y * pixel_height) / 2

            filename = f"{center_lat:.6f}_{center_lon:.6f}.tif"
            output_path = os.path.join(destination_directory, filename)

            driver = gdal.GetDriverByName('GTiff')
            out_raster = driver.Create(output_path, pixels_per_square_x, pixels_per_square_y, 1, gdal.GDT_Float32)
            out_raster.SetGeoTransform((
                min_lon, pixel_width, 0,
                max_lat, 0, pixel_height
            ))
            out_raster.SetProjection(projection)

            outband = out_raster.GetRasterBand(1)
            outband.WriteArray(subset)
            if nodata is not None:
                outband.SetNoDataValue(nodata)

            outband.FlushCache()
            out_raster = None

            current_square += 1
            print(f"Processed {current_square}/{total_squares} squares from {file_path}")

if __name__ == "__main__":
    source_directory = r"J:\GDA\GIS\LandsatEXTRACT"  # Change this to your source folder containing .bil files
    destination_directory = r"J:\GDA\GIS\LandsatDEM-1kmsq"  # Change this to your desired destination folder
    bil_to_geotiff(source_directory, destination_directory)
