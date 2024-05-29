import random
import requests
from geopy.distance import geodesic

def generate_random_coordinates():
    lat = random.uniform(-90, 90)
    lon = random.uniform(-180, 180)
    return lat, lon

def is_on_land(lat, lon):
    url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10'
    response = requests.get(url)
    data = response.json()
    if 'error' in data or 'address' not in data:
        return False
    return 'country' in data['address']

def get_1sqkm_patch(lat, lon):
    center = (lat, lon)
    point_1km_north = geodesic(meters=500).destination(center, 0)
    point_1km_east = geodesic(meters=500).destination(center, 90)
    point_1km_south = geodesic(meters=500).destination(center, 180)
    point_1km_west = geodesic(meters=500).destination(center, 270)
    return {
        'center': center,
        'north': point_1km_north,
        'east': point_1km_east,
        'south': point_1km_south,
        'west': point_1km_west
    }

def main():
    valid_coordinates = False
    while not valid_coordinates:
        lat, lon = generate_random_coordinates()
        if is_on_land(lat, lon):
            valid_coordinates = True
            patch = get_1sqkm_patch(lat, lon)
            print(f'1 sq-km patch center: {patch["center"]}')
            print(f'North point: {patch["north"]}')
            print(f'East point: {patch["east"]}')
            print(f'South point: {patch["south"]}')
            print(f'West point: {patch["west"]}')
        else:
            print(f'Coordinates {lat}, {lon} are not on land. Generating new coordinates.')

if __name__ == "__main__":
    main()
