import requests
import json
from pymongo import MongoClient

BASE_URL_JC_DECAUX = "https://api.jcdecaux.com/vls/v1/"
BASE_URL_AN_ROTHAR_NUA = "https://data.bikeshare.ie/dataapi/resources/station/data/list"
BASE_URL_NEXT_BIKE = "https://api.nextbike.net/maps/nextbike-live.json"
BASE_URL_BLEEPER_BIKES = "https://bleeperbike.staging.derilinx.com/last_snapshot"


def get_stations_jc_decaux(contract, api_key):
    """
    Gets a list of all stations within the specified town/city.
    Results in a GET request to the JC Decaux API using a URL in this format:
    https://api.jcdecaux.com/vls/v1/stations?contract={contract_name}&apiKey={api_key}
    :param contract: The name of the town / city where the scheme operates.
    :param api_key: A unique API key. See https://developer.jcdecaux.com.
    :return: A string of JSON with data related to each JC Decaux bike station in the city
    """
    url = BASE_URL_JC_DECAUX + "stations?contract=" + contract + "&apiKey=" + api_key

    # set up the MongoDB connection
    client = MongoClient('localhost')
    db = client.bikebuddy
    col = db.jc_decaux

    # get the latest list of JC Decaux bike stations
    jc_decaux_stations = call_api('GET', url)

    # transform each station in the list, and insert into mongodb
    for station in jc_decaux_stations:
        create_mongo_doc_jc_decaux(station)
        col.insert_one(station)

def create_mongo_doc_jc_decaux(station):
    # TODO: turn this into a method that transforms a station into a format ready to insert into mongodb
    # turn the "position" attribute into a GeoJSON Point 
    station["position"] = { "type": "Point", "coordinates": [ station["position"]["lng"], station["position"]["lat"] ] }
    return station
    

def get_stations_an_rothar_nua(scheme, api_key):
    """
    Gets a list of An Rothar Nua bike stations.
    :param scheme: The An Rothar Nua ID number for the city of interest, or pass -1 to get all stations.
        Valid scheme IDs are; -1 = All cities, 2 = Cork, 3 = Limerick, 4 = Galway
    :param api_key: An API key that can only be generated on request to An Rothar Nua.
    :return: A string of JSON data relating to each bike station
    """
    valid_scheme_id = {'-1', '2', '3', '4'}
    if str(scheme) not in valid_scheme_id:
        failure_response = {"HTTP Status": 422, "Reason": "Invalid scheme ID.  Scheme ID should be one of %r." % valid_scheme_id}
        return failure_response

    return call_api('POST', BASE_URL_AN_ROTHAR_NUA, {'key': api_key, 'schemeId': scheme})


def get_stations_nextbike(city):
    """
    Gets the data for all bike stations in the NextBike scheme in a specified city.
    :param city: Numeric ID of an individual city in the NextBike database. Belfast is 238.
    :return: A JSON string with some metadata, and data relating to each station in the city.
    """
    return call_api('GET', BASE_URL_NEXT_BIKE + "?city=" + str(city))


def get_bikes_bleeperbikes():
    """
    Gets a list of all Bleeper Bikes in Dublin.  No API key is needed.
    :return: A list of Bleeper Bikes
    """
    return call_api('GET', BASE_URL_BLEEPER_BIKES)


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
        failure_response = {"HTTP Status": 422, "Reason": "http_verb must be either GET or POST"}
        return failure_response

    # The Bleeper Bikes API returns 201 for successful responses
    if response.status_code in {200, 201}:
       return response.json()
    else:
        failure_response = {"HTTP Status": response.status_code, "Reason": response.reason}
        return failure_response