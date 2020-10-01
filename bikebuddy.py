from flask import Flask, request
import yaml
from operator_api_client.api_client import *

app = Flask(__name__)


def read_app_settings():
    """
    Open and read the YAML config file for the application.
    :return: The contents of the YAML config file
    """
    document = open('config/config.yaml', 'r')
    return yaml.load(document, Loader=yaml.FullLoader)


# Get important configuration details from a .yaml file
app_settings = read_app_settings()

# JC Decaux & An Rothar Nua both require an API key to be provided
API_KEY_JC_DECAUX = app_settings['operator_api_keys'].get('jc_decaux')
API_KEY_AN_ROTHAR_NUA = app_settings['operator_api_keys'].get('an_rothar_nua')


@app.route('/getupdates/stations/jcdecaux/<contract>')
def update_stations_jc_decaux(contract):
    return update_jc_decaux(contract, API_KEY_JC_DECAUX)


@app.route('/getupdates/stations/anrotharnua/<scheme>')
def update_stations_an_rothar_nua(scheme):
    return update_an_rothar_nua(scheme, API_KEY_AN_ROTHAR_NUA)


@app.route('/getupdates/stations/nextbike/<city>')
def update_stations_nextbike(city):
    return update_nextbike(city)


@app.route('/getupdates/bikes/bleeperbikes')
def update_bikes_bleeperbikes():
    return update_bleeperbikes()

if __name__ == '__main__':
    app.run(debug=True)