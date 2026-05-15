"""Geocoding helpers reused by spatial controllers."""

import requests


def request_nominatim(url, params, headers, timeout):
    return requests.get(url, params=params, headers=headers, timeout=timeout)
