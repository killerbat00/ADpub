# !/usr/bin/env python
# -*- coding: utf-8 -*-

import platform

"""
ADpub is a simple publishing service written using Python and chalice and deployed to AWS Lambda.
"""

from chalice import Chalice

app = Chalice(app_name='adpub')
app.debug = True


@app.route('/status')
def status():
    """
    :return: Status information about the ADpub service.
    """
    resp = {"status": "OK",
            "images_uploaded": 0}

    deployment_info = {"machine": platform.machine(), "platform": platform.platform(),
                       "processor": platform.processor()}

    resp["deployment_info"] = deployment_info
    return resp


@app.route('/breweries')
def breweries():
    """
    :return: Status information about the ADpub service.
    """
    return {"hello": "world!"}


@app.route('/image', methods=['POST'])
def image():
    """
    :return: Status information about the ADpub service.
    """
    return {"hello": "world!"}
