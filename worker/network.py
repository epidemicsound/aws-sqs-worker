import json
import requests


class APIError(Exception):
    def __init__(self, message, status_code, response):
        self.message = message
        self.status_code = status_code
        self.response = response


# HTTP requests utils
def make_post(path, data, headers={}):
    response = requests.post(path, data=data, headers=headers)
    if response.status_code >= 300:
        raise APIError(
            'POST failed: {}'.format(response.text),
            response.status_code,
            response
        )

    return response


def make_post_json(path, data, headers={}):
    headers['Content-Type'] = 'application/json'
    return make_post(path, json.dumps(data), headers)


def make_get(path, headers={}):
    response = requests.get(path, headers=headers)
    if response.status_code >= 300:
        raise APIError(
            'GET failed: {}'.format(response.text),
            response.status_code,
            response
        )

    return response
