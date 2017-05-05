# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ADpub is a simple publishing service written using Python and chalice and
deployed to AWS Lambda.
See README.md for full documentation on the service endpoints.
"""
import base64
import platform
import uuid
from typing import Optional

import boto3
import botocore
import requests
from chalice import Chalice

from chalicelib import BREWERY_KEY, S3_BUCKET

app = Chalice(app_name='adpub')
app.debug = True

failure_resp = {"status": "failure"}
S3 = boto3.client('s3')


@app.route('/status')
def status() -> dict:
    """
    :return: Status information about the ADpub service.
    """
    try:
        s3_resp = S3.get_object(Bucket=S3_BUCKET, Key="Uploads")
        num_uploads = int(s3_resp["Body"].read())
    except (botocore.exceptions.ClientError, KeyError):
        num_uploads = 0

    response = {"status": "OK",
                "images_uploaded": num_uploads}

    deployment_info = {"machine": platform.machine(),
                       "platform": platform.platform(),
                       "processor": platform.processor()}

    response["deployment_info"] = deployment_info
    return response


@app.route('/breweries')
def breweries() -> dict:
    """
    The breweries route will return breweries that are near location of the
    IP address that requested the route. It does so by first utilizing the
    ip-api.com IP geolocation service and passing the location into
    BreweryDB.com's location API.

    :return: A JSON encoded list of breweries near the request's IP
    """
    success_resp = {"status": "OK"}
    request_ip = None
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
def image() -> dict:
    """
    :return: Status information about the ADpub service.
    """
    body = app.current_request.json_body

    if not body:
        return failure_resp

    image_data = body.get("data")
    if not image_data:
        return failure_resp

    image_data = base64.b64decode(image_data)
    # upload image to S3, return URL
    filename = f"{uuid.uuid4()}.png"
    try:
        S3.put_object(
            Bucket=S3_BUCKET,
            Key=filename,
            Body=image_data,
            ACL="public-read",
            ContentType="image/png"
        )
    except botocore.exceptions.ClientError:
        return failure_resp

    try:
        s3_resp = S3.get_object(Bucket=S3_BUCKET, Key="Uploads")
        # ints are not valid values for S3
        num_uploads = str(int(s3_resp["Body"].read()) + 1)
    except (botocore.exceptions.ClientError, KeyError):
        num_uploads = "1"

    try:
        S3.put_object(Bucket=S3_BUCKET, Key="Uploads", Body=num_uploads)
    except botocore.exceptions.ClientError:
        return failure_resp

    return {"status": "ok",
            "data": {
                "url": f"https://s3.amazonaws.com/{S3_BUCKET}/{filename}"
            }}


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
