"""
Wrapper for http requests
"""
import requests

from lifeguard.settings import HTTP_PROXY, HTTPS_PROXY


def get(url, headers=None, auth=None):
    """
    :param url:
    :param headers:

    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    request_args = {"url": url, "headers": headers, "auth": auth}
    __append_proxies(request_args)
    return requests.get(**request_args)


def post(url, data=None, headers=None, auth=None):
    """
    :param url:
    :param data:
    :param headers:

    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    request_args = {"url": url, "headers": headers, "data": data, "auth": auth}
    __append_proxies(request_args)
    return requests.post(**request_args)


def __append_proxies(request_args):
    proxies = {
        "http": HTTP_PROXY,
        "https": HTTPS_PROXY,
    }

    keys_to_remove = [key for key in proxies.keys() if not proxies[key]]
    for key in keys_to_remove:
        proxies.pop(key)

    if proxies:
        request_args["proxies"] = proxies
