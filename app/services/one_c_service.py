from app.services import *
from config import *
import base64

URL = ONE_C_URL

def get_depots_list():
    # make credentials for base Distribution
    url = URL + '/Distribution/hs/truck_checkbot/depot_list'
    username = ONE_C_DISTRIBUTION_LOGIN
    password = ONE_C_DISTRIBUTION_PASSWORD
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    # create auth by username and password
    basic_auth_token = f"Basic {encoded_credentials}"
    headers = {
        'Authorization': basic_auth_token,
        'Content-Type': 'application/json'
    }
    # send request
    response = requests.get(url, headers=headers)
    content = json.loads(response.content)
    return content

def get_cars_list():
    # make credentials for base Distribution
    url = URL + '/MilkNew/hs/truck_checkbot/cars_list/'
    username = ONE_C_MILKNEW_LOGIN
    password = ONE_C_MILKNEW_PASSWORD
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    # create auth by username and password
    basic_auth_token = f"Basic {encoded_credentials}"
    headers = {
        'Authorization': basic_auth_token,
        'Content-Type': 'application/json'
    }
    # send request
    response = requests.get(url, headers=headers)
    content = json.loads(response.content)
    return content

