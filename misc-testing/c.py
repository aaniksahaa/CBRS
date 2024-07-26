import json

# Path to your GeoJSON file
geojson_file_path = 'districts.geojson'

def count_features_in_geojson(file_path):
    with open(file_path, 'r') as file:
        # Load GeoJSON data from file
        geojson_data = json.load(file)
        
        # Access the features array
        features = geojson_data.get('features', [])
        
        # Return the number of features
        return len(features)

# Get the number of features
number_of_features = count_features_in_geojson(geojson_file_path)

print(f"Number of features in the GeoJSON file: {number_of_features}")
