from utils.http_utils import *


BASE_URL_JC_DECAUX = "https://api.jcdecaux.com/vls/v1/"
BASE_URL_AN_ROTHAR_NUA = "https://data.bikeshare.ie/dataapi/resources/station/data/list"
BASE_URL_NEXT_BIKE = "https://api.nextbike.net/maps/nextbike-live.json"
BASE_URL_BLEEPER_BIKES = "https://bleeperbike.staging.derilinx.com/last_snapshot"


def get_stations_jc_decaux(contract, api_key):
    """
    Gets a list of all stations within a specific contract, i.e. in a town or city.
    It makes a GET request to the JC Decaux API using a URL in the following format:
    https://api.jcdecaux.com/vls/v1/stations?contract={contract_name}&apiKey={api_key}
    :param contract: The name of the town / city where the particular bike share scheme operates.
    :param api_key: A unique API key. See https://developer.jcdecaux.com.
    :return: A list of bike stations belonging to the particular contract, where each bike station's data is a dict
    """
    url = BASE_URL_JC_DECAUX + "stations?contract=" + contract + "&apiKey=" + api_key
    return call_api('GET', url)


def get_stations_an_rothar_nua(scheme, api_key):
    """
    Gets a list of bike stations operated by An Rothar Nua, either in a particular city or in all cities.
    :param scheme: The An Rothar Nua ID number for the city of interest, or pass -1 to get all stations.
        Valid scheme IDs are; -1 = All cities, 2 = Cork, 3 = Limerick, 4 = Galway
    :param api_key: An API key that can only be generated on request to An Rothar Nua.
    :return: A dictionary with some metadata, and a list of individual bike stations.
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
    :return: A dictionary containing some metadata, and data relating to each station in the city.
    """
    return call_api('GET', BASE_URL_NEXT_BIKE + "?city=" + str(city))


def get_bikes_bleeperbikes():
    """
    Gets a list of all stations within a specific contract, i.e. in a town or city.
    It makes a GET request to the JC Decaux API using a URL in the following format:
    https://api.jcdecaux.com/vls/v1/stations?contract={contract_name}&apiKey={api_key}
    :param contract: The name of the town / city where the particular bike share scheme operates.
    :param api_key: A unique API key. See https://developer.jcdecaux.com.
    :return: A list of bike stations belonging to the particular contract, where each bike station's data is a dict
    """
    return call_api('GET', BASE_URL_BLEEPER_BIKES)