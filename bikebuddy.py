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

# Main API methods will go here

if __name__ == '__main__':
    app.run(debug=True)