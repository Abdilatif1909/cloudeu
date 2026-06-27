import logging

from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        logger.exception("Unhandled API error", exc_info=exc)
        return response
    response.data = {
        "success": False,
        "status_code": response.status_code,
        "errors": response.data,
    }
    return response
