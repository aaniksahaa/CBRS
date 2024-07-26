import math

class Coord:
    def __init__(self, latitude, lat_direction, longitude, long_direction):
        self.latitude = self._convert_to_decimal(latitude, lat_direction)
        self.longitude = self._convert_to_decimal(longitude, long_direction)
        self.lat_direction = lat_direction
        self.long_direction = long_direction

    def _convert_to_decimal(self, degrees, direction):
        decimal = float(degrees)
        if direction in ['S', 'W']:
            decimal *= -1
        return decimal

    def haversine_distance(self, other):
        # Radius of the Earth in kilometers
        R = 6371.0

        lat1_rad = math.radians(self.latitude)
        lon1_rad = math.radians(self.longitude)
        lat2_rad = math.radians(other.latitude)
        lon2_rad = math.radians(other.longitude)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance
    
    def __str__(self) -> str:
        return f'Latitude: {abs(self.latitude)} {self.lat_direction}, Longitude: {abs(self.longitude)} {self.long_direction}'

    def to_dict(self):
        return {
            'latitude': abs(self.latitude),
            'lat_direction': self.lat_direction,
            'longitude': abs(self.longitude),
            'long_direction': self.long_direction
        }

    @classmethod
    def from_dict(cls, coord_dict):
        return cls(
            coord_dict['latitude'], 
            coord_dict['lat_direction'], 
            coord_dict['longitude'], 
            coord_dict['long_direction']
        )

if __name__ == "__main__":
    # Example usage:
    coord1 = Coord("52.2296756", "N", "21.0122287", "W")
    coord2 = Coord("41.8919300", "N", "12.5113300", "W")

    print(coord2)

    distance = coord1.haversine_distance(coord2)
    print(f"Distance: {distance} km")

    # Example usage
    coord1 = Coord(23.8103, 'N', 90.4125, 'E')
    print(coord1.to_dict())
    # Output: {'latitude': 23.8103, 'lat_direction': 'N', 'longitude': 90.4125, 'long_direction': 'E'}

    coord_dict = {'latitude': 23.8103, 'lat_direction': 'N', 'longitude': 90.4125, 'long_direction': 'E'}
    coord2 = Coord.from_dict(coord_dict)
    print(coord2)
    # Output: Latitude: 23.8103 N, Longitude: 90.4125 E
