import requests


def post(url, data=None, headers=None):
    requests.post(url=url, data=data, headers=headers)
