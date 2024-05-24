import aiohttp_session
from aiohttp.web_exceptions import HTTPException, HTTPUnauthorized
from aiohttp.web_middlewares import middleware
from aiohttp_apispec import validation_middleware

from admin_app.web.utils import error_json_response


@middleware
async def error_handling_middleware(request, handler):
    try:
        response = await handler(request)
    except HTTPException as e:
        request.app.logger.error(e.reason, exc_info=e)
        return error_json_response(
            http_status=e.status, status=e.reason, message=e.reason, data=e.text
        )
    except Exception as e:
        request.app.logger.error("Exception", exc_info=e)
        return error_json_response(
            http_status=500, status=str(e), message=str(e)
        )

    return response


def require_login(func):
    func.__require_login__ = True
    return func


@middleware
async def check_login(request, handler):
    require_login = getattr(handler, "__require_login__", False)
    session = await aiohttp_session.get_session(request)
    admin_session = session.get("admin")
    if require_login:
        if not admin_session:
            raise HTTPUnauthorized
        if not await request.app.store.admin.get_by_email(
            admin_session["email"]
        ):
            raise HTTPUnauthorized

    return await handler(request)


def setup_middlewares(app):
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(validation_middleware)
    app.middlewares.append(check_login)
