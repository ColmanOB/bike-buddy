import os
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


@app.route('/jc_decaux/stations/<contract>')
def stations_jc_decaux(contract):
    return str(get_stations_jc_decaux(contract, API_KEY_JC_DECAUX))


@app.route('/an_rothar_nua/stations/<scheme>')
def stations_an_rothar_nua(scheme):
    return str(get_stations_an_rothar_nua(scheme, API_KEY_AN_ROTHAR_NUA))


@app.route('/nextbike/stations/<city>')
def stations_nextbike(city):
    return str(get_stations_nextbike(city))


if __name__ == '__main__':
    app.run(debug=True)