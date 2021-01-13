"""Utility functions
"""
import os
import re
from urllib.parse import urlencode, urlunparse, urlparse

import toolz
import requests
from flask import request


def slurp(path: str) -> str:
    """
    Reads a file given a relative or absolute path
    """
    abs_path = os.path.abspath(path)
    with open(abs_path, encoding="utf-8-sig") as file:
        return file.read()


def create_headers(resp: requests.Response, request_params: dict, status_code: int) -> dict:
    """Create various custom headers that need to be added to a PostgREST response.
    Args:
        resp (requests.Response): PostgREST response.
        request_params (dict): Request params.
        status_code (int): Status code of the PostgREST response.
    Returns:
        dict: Headers.
    """
    # Remove excluded headers
    excluded_headers = ['content-encoding', 'transfer-encoding']
    headers = {name: val for name, val in resp.raw.headers.items(
    ) if name.lower() not in excluded_headers}

    if status_code >= 300:
        return headers

    assert "Content-Range" in headers, "Content-Range is missing from header?"
    content_range_header = headers['Content-Range']

    link_header = create_link_header(resp,
                                     request_params,
                                     content_range_header)

    return {
        **headers,
        **link_header,
    }


def create_link_header(resp: requests.Response,
                       request_params: dict,
                       content_range_header: str) -> dict:
    """Create the link header that will provide pagination for the client.
    Args:
        resp (requests.Response): PostgREST response.
        request_params (dict): Request params.
        content_range_header (dict): Content-Range header from postgREST.
    Returns:
        dict: Link header.
    """
    link_header = []

    limit_q = request_params.get("limit", None)
    try:
        limit = int(limit_q)
    except (TypeError, ValueError):
        # No limit found, just return
        return {}

    try:
        # if _ is assigned, it will be the total length of the response
        response_len, _ = content_range_header.split("/")
        response_range = re.findall(r'\d+', response_len)
        response_range_int = [int(i) for i in response_range]
        total_range = (response_range_int[1] - response_range_int[0]) + 1
    except IndexError:
        # This will happen if we can't find a number value in the Content-Range header
        return {}

    results = resp.json()
    if results and total_range == limit:
        # When do we create a next link header?
        #   1. If results has data
        #   2. If the Content-Range is equal to the limit in the query
        #       ex. Content-Range=0-9/* and limit=10
        last_item = results[-1]
        last_id = last_item.get("int_id", None)
        if last_id:
            last_id = results[-1]["int_id"]
            next_link = create_next_link_header(last_id, request_params)
            link_header.append(next_link)

    if link_header:
        " ".join(link_header)
        return {"Link": link_header}

    return {}


def create_next_link_header(last_id: int, request_params: dict) -> str:
    """Create the next link header.
    Args:
        last_id (int): `int_id` of the last item returned in the current request.
        request_params (dict): Request params.
    Returns:
        str: Next link.
    """
    next_page_params = {**request_params, "int_id": f"gt.{last_id}"}

    next_request_url = toolz.pipe(request.url,
                                  urlparse,
                                  lambda req_url: req_url._replace(
                                      query=urlencode(next_page_params)),
                                  urlunparse)

    return f'<{next_request_url}>; rel="next"'
