from aiohttp import web
from aiohttp.abc import Request
from aiohttp.web_exceptions import HTTPException
from aiohttp.web_middlewares import middleware
from aiohttp_apispec import validation_middleware

from app.web.utils import error_json_response


@web.middleware
async def example_mw(request: Request, handler):
    return await handler(request)


@middleware
async def error_handling_middleware(request: "Request", handler):
    try:
        response = await handler(request)
    except HTTPException as e:
        request.app.logger.error(e.reason, exc_info=e)
        return error_json_response(
            http_status=e.status,
            status=e.reason,
            message=e.reason,
            data=e.text
        )
    except Exception as e:
        request.app.logger.error('Exception', exc_info=e)
        return error_json_response(
            http_status=500,
            status=str(e),
            message=str(e)
        )

    return response


def setup_middlewares(app):
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(validation_middleware)
