import os
import glob
import fiona
from shapely.geometry import shape
from osgeo import gdal

def clip_dem_with_squares(squares_shapefile, dem_directory, output_directory):
    # Read the squares from the shapefile
    with fiona.open(squares_shapefile, 'r') as src:
        squares = [shape(feature['geometry']) for feature in src]

    if not squares:
        print("No squares found in the shapefile.")
        return

    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Get list of all .bil files in the DEM directory
    dem_files = glob.glob(os.path.join(dem_directory, '*.bil'))

    if not dem_files:
        print("No .bil files found in the DEM directory.")
        return

    # Iterate over each square and clip the intersecting DEM files
    for i, square in enumerate(squares):
        # Get the bounding box of the square
        minx, miny, maxx, maxy = square.bounds
        print(f"Processing square {i+1}/{len(squares)}: {minx}, {miny}, {maxx}, {maxy}")

        # Find intersecting DEM files
        for dem_file in dem_files:
            dem_ds = gdal.Open(dem_file)
            dem_transform = dem_ds.GetGeoTransform()
            dem_projection = dem_ds.GetProjection()

            # Get DEM boundaries
            dem_minx = dem_transform[0]
            dem_maxx = dem_transform[0] + dem_transform[1] * dem_ds.RasterXSize
            dem_miny = dem_transform[3] + dem_transform[5] * dem_ds.RasterYSize
            dem_maxy = dem_transform[3]

            # Check if the DEM file intersects with the square
            if dem_minx < maxx and dem_maxx > minx and dem_miny < maxy and dem_maxy > miny:
                print(f"Clipping {dem_file}...")

                # Clip the DEM file
                output_file = os.path.join(output_directory, f"clipped_square_{i+1}.tif")
                gdal.Warp(output_file, dem_file, format="GTiff",
                          outputBounds=[minx, miny, maxx, maxy],
                          dstSRS=dem_projection)

    print("Clipping completed.")

if __name__ == "__main__":
    squares_shapefile = r"C:\Users\giegi\OneDrive - The Ohio State University\Qin\W6\30KSquares.shp"  # Change this to your shapefile containing the squares
    dem_directory = r"J:\GDA\GIS\LandsatEXTRACT"  # Change this to your DEM files directory
    output_directory = r"J:\GDA\GIS\Landsat30KClips"  # Change this to your desired output directory
    clip_dem_with_squares(squares_shapefile, dem_directory, output_directory)