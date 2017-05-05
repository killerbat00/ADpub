# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ADpub is a simple publishing service written using Python and chalice and
deployed to AWS Lambda.
See README.md for full documentation on the service endpoints.
"""

import platform
from typing import Optional

import requests
from chalice import Chalice

from chalicelib import BREWERY_KEY

app = Chalice(app_name='adpub')
app.debug = True


@app.route('/status')
def status():
    """
    :return: Status information about the ADpub service.
    """
    resp = {"status": "OK",
            "images_uploaded": 0}

    deployment_info = {"machine": platform.machine(),
                       "platform": platform.platform(),
                       "processor": platform.processor()}

    resp["deployment_info"] = deployment_info
    return resp


@app.route('/breweries')
def breweries():
    """
    The breweries route will return breweries that are near location of the
    IP address that requested the route. It does so by first utilizing the
    ip-api.com IP geolocation service and passing the location into
    BreweryDB.com's location API.

    :return: A JSON encoded list of breweries near the request's IP
    """
    request_ip = None
    failure_resp = {"status": "failure"}
    success_resp = {"status": "OK"}
    current_request = app.current_request.to_dict()

    # Look for the first IP address in the X-Forwarded-For HTTP Header
    headers = current_request.get("headers")
    if headers:
        forwarded_for = headers.get("x-forwarded-for")
        if forwarded_for:
            request_ip = forwarded_for.split(",")[0]

    if not request_ip:
        return failure_resp

    city = _find_city(request_ip)

    if not city:
        return failure_resp

    brewery_data = _find_breweries(city)

    if not brewery_data:
        return failure_resp

    success_resp["data"] = []

    for i in brewery_data.get("data"):
        info = {"name": i["brewery"].get("name"),
                "website": i["brewery"].get("website"),
                "phone": i.get("phone"),
                "street_address": i.get("streetAddress"),
                "postal_code": i.get("postalCode")}
        success_resp["data"].append(info)

    return success_resp


@app.route('/image', methods=['POST'])
def image():
    """
    :return: Status information about the ADpub service.
    """
    return {"hello": "world!"}


def _find_city(ip: str) -> Optional[str]:
    """
    Uses ip-api to find the city in which an IP address is located.

    :param ip: the ip address to geolocate
    :return:   the city where theIP address is located or None
    """
    geo_ip_url = "http://ip-api.com/json/"

    # Query ip-api's geolocation API to locate the request's IP
    try:
        r = requests.get(f"{geo_ip_url}/{ip}")
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        return

    geo_resp = r.json()
    if geo_resp.get("status") != "success":
        return

    return geo_resp.get("city")


def _find_breweries(city: str) -> Optional[dict]:
    """
    Uses the BreweryDB API to find all breweries located in a given city.
    the name, website, phone number, street address and ZIP code are
    parsed from the API's response and returned in a list.

    :param city: the city for which to search for breweries
    :return:     a list of dictionaries each containing data on a brewery
    """
    brewery_url = "http://api.brewerydb.com/v2/"

    params = {"key": BREWERY_KEY,
              "locality": city}

    # Query Brewery DB's application to locate local breweries
    try:
        r = requests.get(f"{brewery_url}/locations", params=params)
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        return

    brewery_resp = r.json()
    if brewery_resp.get("status") != "success":
        return

    if int(brewery_resp.get("totalResults", 0)) == 0:
        return

    return brewery_resp
