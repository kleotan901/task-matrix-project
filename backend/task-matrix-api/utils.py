from rest_framework.views import exception_handler
from http import HTTPStatus
from typing import Any

from rest_framework.views import Response


def api_exception_handler(exc: Exception, context: dict[str, Any]) -> Response:
    """Custom API exception handler."""

    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # Using the description's of the HTTPStatus class as error message.
        http_code_to_message = {
            element.value: element.description for element in HTTPStatus
        }

        error_payload = {
            "error": {
                "status_code": 0,
                "message": "",
                "details": [],
            }
        }

        error_payload["error"]["status_code"] = response.status_code
        error_payload["error"]["message"] = http_code_to_message[response.status_code]
        error_payload["error"]["details"] = response.data

        response.data = error_payload

    return response
