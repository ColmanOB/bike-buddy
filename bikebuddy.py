from flask import Flask, request
import yaml
from operator_api_client.api_client import *
from operator_api_client.db_updaters import db_updaters

app = Flask(__name__)
app.register_blueprint(db_updaters)


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

if __name__ == '__main__':
    app.run(debug=True)