import requests
import json
from pymongo import MongoClient
from flask import jsonify

BASE_URL_JC_DECAUX = "https://api.jcdecaux.com/vls/v1/"
BASE_URL_AN_ROTHAR_NUA = "https://data.bikeshare.ie/dataapi/resources/station/data/list"
BASE_URL_NEXT_BIKE = "https://api.nextbike.net/maps/nextbike-live.json"
BASE_URL_BLEEPER_BIKES = "https://bleeperbike.staging.derilinx.com/last_snapshot"


def get_stations_jc_decaux(contract, api_key):
    """
    Gets a list of all JC Decaux bike stations within the specified town/city.
    Results in a GET request to the JC Decaux API using a URL in this format:
    https://api.jcdecaux.com/vls/v1/stations?contract={contract_name}&apiKey={api_key}
    :param contract: The name of the town / city where the scheme operates.
    :param api_key: A unique API key. See https://developer.jcdecaux.com.
    :return: A string of JSON with data related to each JC Decaux bike station in the city
    """
    SCHEME_OPERATOR = "jc_decaux"
    # Build the URL and call the JC Decaux API
    url = BASE_URL_JC_DECAUX + "stations?contract=" + contract + "&apiKey=" + api_key
    stations = call_api('GET', url)

    # Transform the location of each station to a GeoJSON point
    for station in stations:
        create_geojson_point(SCHEME_OPERATOR, station)

    # Update the list of JC Decaux stations in the database
    return update_stations(SCHEME_OPERATOR, stations)


def get_stations_an_rothar_nua(scheme, api_key):
    """
    Gets a list of An Rothar Nua bike stations.
    :param scheme: The An Rothar Nua ID number for the city of interest, or pass -1 to get all stations.
        Valid scheme IDs are; -1 = All cities, 2 = Cork, 3 = Limerick, 4 = Galway
    :param api_key: An API key that can only be generated on request to An Rothar Nua.
    :return: A string of JSON data relating to each bike station
    """
    SCHEME_OPERATOR = "an_rothar_nua"
    valid_scheme_id = {'-1', '2', '3', '4'}
    if str(scheme) not in valid_scheme_id:
        return {
            "HTTP Status": 422, 
            "Reason": "Invalid scheme ID.  Scheme ID should be one of %r." % valid_scheme_id
        }

    # Get the list of all stations from the An Rothar Nua API
    stations = call_api('POST', BASE_URL_AN_ROTHAR_NUA, {'key': api_key, 'schemeId': scheme})

    # Transform the location data of each station to a GeoJSON point
    for station in stations["data"]:
        create_geojson_point(SCHEME_OPERATOR, station)

    # Update any An Rothar Nua stations with changes, and return a summary of the database operations
    return update_stations(SCHEME_OPERATOR, stations["data"])


def get_stations_nextbike(city):
    """
    Gets the data for all bike stations in the NextBike scheme in a specified city.
    :param city: Numeric ID of an individual city in the NextBike database. Belfast is 238.
    :return: A JSON string with some metadata, and data relating to each station in the city.
    """
    SCHEME_OPERATOR = "nextbike"
    stations = call_api('GET', BASE_URL_NEXT_BIKE + "?city=" + str(city))
    
    # Transform the location data of each station to a GeoJSON point
    # Nextbike returns the stations within a complex nested structure
    for station in stations["countries"][0]["cities"][0]["places"]:
        create_geojson_point(SCHEME_OPERATOR, station)

    # Update any Nextbike stations with changes, and return a summary of the database operations
    return update_stations(SCHEME_OPERATOR, stations["countries"][0]["cities"][0]["places"])


def get_bikes_bleeperbikes():
    """
    Gets a list of all Bleeper Bikes in Dublin.  No API key is needed.
    :return: A list of Bleeper Bikes
    """
    #return call_api('GET', BASE_URL_BLEEPER_BIKES)
    SCHEME_OPERATOR = "bleeper_bikes"
    bikes = call_api('GET', BASE_URL_BLEEPER_BIKES)

    for bike in bikes:
        create_geojson_point(SCHEME_OPERATOR, bike)

    return update_bikes(SCHEME_OPERATOR, bikes)


def call_api(http_verb, url, request_parameters=None):
    """
    Makes the HTTPS request to an operator API and returns the JSON response.
    :param http_verb: Either GET or POST, depending on what the individual API expects
    :param url: The scheme operator's URL for the resource to be retrieved
    :param request_parameters: Used where the request is a POST with parameters in the body
    :return: A string of JSON data from the scheme operator's API
    """
    if http_verb.lower() == 'get':
        response = requests.get(url, timeout=10)
    elif http_verb.lower() == 'post':
        response = requests.post(url, data=request_parameters, timeout=10)
    else:
        failure_response = {
            "HTTP Status": 422, 
            "Reason": "http_verb must be either GET or POST"
        }
        return jsonify(failure_response)

    # The Bleeper Bikes API returns 201 for successful responses
    if response.status_code not in {200, 201}:
        failure_response = {
            "HTTP Status": response.status_code, 
            "Reason": response.reason
        }
        return jsonify(failure_response)

    # If we got this far, we should have a successful HTTP response to return    
    return response.json()


def update_stations(operator, stations):
    """
    Connects to the database and does an upsert for each station passed in.
    """
    # Connect to MongoDB & specify a collection based on the operator argument provided
    with MongoClient('localhost') as client:
        db = client.bikebuddy
        col = db[operator]
        # Used to gather database operation results
        matched_count = 0
        modified_count = 0

        for station in stations:
            # The matching criterion for the update varies depending on the scheme operator
            if operator == "an_rothar_nua":
                result = col.update_one(
                    {"stationId" : station["stationId"]},
                    {"$set": station},
                    upsert=True
                )
            elif operator == "jc_decaux":
                result = col.update_one(
                    {"number" : station["number"]},
                    {"$set": station},
                    upsert=True
                )
            elif operator == "nextbike":
                result = col.update_one(
                    {"uid" : station["uid"]},
                    {"$set": station},
                    upsert=True
                )
            # Increment counters for the summary of database operations
            matched_count += result.matched_count
            modified_count += result.modified_count
        # Put together a summary of how many records were updated 
        summary = {
            "matched": matched_count,
            "modified": modified_count,
        }
        return jsonify(summary)


def update_bikes(operator, bikes):
    """
    Connects to the database and does an upsert for each station passed in.
    """
    # Connect to MongoDB & specify a collection based on the operator argument provided
    with MongoClient('localhost') as client:
        db = client.bikebuddy
        col = db[operator]
        # Used to gather database operation results
        matched_count = 0
        modified_count = 0

        for bike in bikes:
            # The matching criterion for the update varies depending on the scheme operator
            if operator == "bleeper_bikes":
                result = col.update_one(
                    {"frame_id" : bike["frame_id"]},
                    {"$set": bike},
                    upsert=True
                )
            # Increment counters for the summary of database operations
            matched_count += result.matched_count
            modified_count += result.modified_count
        # Put together a summary of how many records were updated 
        summary = {
            "matched": matched_count,
            "modified": modified_count,
        }
        return jsonify(summary)


def create_geojson_point(operator, entity):
    """ 
    Transforms a pair of latitude and longitude values to a GeoJSON point.
    This facilitates geospatial operations in MongoDB.
    Where to find the location data varies per scheme operator.
    """
    if operator == "jc_decaux": 
        entity["position"] = {
            "type": "Point", 
            "coordinates": [ 
                entity["position"]["lng"], 
                entity["position"]["lat"] 
            ] 
        }
    elif operator in ("an_rothar_nua", "bleeper_bikes"):
        entity["position"] = {
            "type": "Point", 
            "coordinates": [ 
                entity["longitude"], 
                entity["latitude"]
            ] 
        }
    elif operator == "nextbike":
        entity["position"] = {
            "type": "Point", 
            "coordinates": [ 
                entity["lng"], 
                entity["lat"] 
            ] 
        }
        """
    elif operator == "bleeper_bikes":
        entity["position"] = {
            "type": "Point", 
            "coordinates": [ 
                entity["longitude"], 
                entity["latitude"] 
            ] 
        }
        """
    return entity
