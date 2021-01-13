"""PostgREST proxy
"""
from urllib.parse import urljoin
import traceback

from flask import Response, current_app, request
import requests

from src.api import api_bp
from src.logger import logger
from src import utils
from src.api.error_handlers import ServerError, PostgrestHTTPException


@api_bp.route('/<path:path>', methods=['GET'])
def get_postgrest_proxy(path: str) -> Response:
    """Proxy for PostgREST that modifies various parts of the request,
    such as query params and headers.
    Args:
        path (str): URL path that corresponds to a PostgREST route
    Returns:
        Response: Flask response that mimicks the PostgREST response.
    """

    config = current_app.config['CONFIG']
    postgrest_host = config['postgrest']['host']
    postgrest_url = urljoin(postgrest_host, path)

    # routes_to_modify_query_params = ["products", "outfits", "outfit_thumbnails"]
    # if path in routes_to_modify_query_params:
    #     query_params = modify_query_params(request.args, postgrest_host)
    # else:
    #     query_params = request.args
    query_params = request.args

    # Send PostgREST the same request we received but with modified query params
    try:
        postgrest_resp = requests.request(
            method=request.method,
            url=postgrest_url,
            headers={key: value for (key, value)
                     in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            params=query_params
        )
    except requests.exceptions.ConnectionError as err:
        logger.error(traceback.format_exc())
        raise ServerError(503, hint="Could not connect to Postgrest.") from err

    postgrest_status_code = postgrest_resp.status_code
    # Abort if we get an error code.
    if postgrest_status_code >= 300:
        raise PostgrestHTTPException(postgrest_resp)

    # Create new headers
    headers = utils.create_headers(postgrest_resp,
                                   query_params,
                                   postgrest_status_code)

    # Create response to send back to client
    response = Response(postgrest_resp.content,
                        postgrest_status_code,
                        headers)

    return response
