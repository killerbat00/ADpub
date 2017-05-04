# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ADpub is a simple publishing service written using Python and chalice and deployed to AWS Lambda.
"""

from chalice import Chalice

app = Chalice(app_name='adpub')


@app.route('/status')
def status():
    """
    :return: Status information about the ADpub service.
    """
    return {"hello": "world!"}


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
