"""Routing helpers reused by spatial controllers."""

import requests


def request_osrm(url, params, headers, timeout):
    return requests.get(url, params=params, headers=headers, timeout=timeout)
