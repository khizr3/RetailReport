"""
This is a helper file that creates a DataSources object with loaded data stored as object variables

Author: Khizr Ali Khizr89@gmail.com

Created: June 9th, 2022
"""
# Imports
from googleplaces import GooglePlaces, types, lang
import config
import requests
import json


class Competition:
    def __init__(self, location_coordinates):
        self.API_KEY = config.PLACES_API_KEY
        self.lat = location_coordinates[0]
        self.long = location_coordinates[1]

    def get_competition(self):

        # Initialising the GooglePlaces constructor
        google_places = GooglePlaces(self.API_KEY)
        query_result = google_places.nearby_search(
            lat_lng={'lat': self.lat, 'lng': self.long},
            radius=5000,
            types=[types.TYPE_GAS_STATION])

        if query_result.has_attributions:
            print(query_result.html_attributions)

        # Iterate over the search results
        for place in query_result.places:
            print(place)
            # place.get_details()
            print(place.name)
            print("Latitude", place.geo_location['lat'])
            print("Longitude", place.geo_location['lng'])
            print()
