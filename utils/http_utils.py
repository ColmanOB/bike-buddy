import requests

def call_api(http_verb, url, request_parameters=None):
    if http_verb.lower() == 'get':
        response = requests.get(url, timeout=10)
    elif http_verb.lower() == 'post':
        response = requests.post(url, data=request_parameters, timeout=10)
    else:
        failure_response = {"HTTP Status": 422, "Reason": "http_verb must be either GET or POST"}
        return failure_response

    # The Bleeper Bikes API returns 201 for successful responses
    if response.status_code in {200, 201}:
       return response.text
    else:
        failure_response = {"HTTP Status": response.status_code, "Reason": response.reason}
        return failure_response