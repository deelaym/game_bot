import os

from aiohttp.web import run_app

from admin_app.web.admin_app import setup_app

if __name__ == "__main__":
    run_app(
        setup_app(
            config_path=os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "etc/config.yaml"
            )
        ), port=8080
    )
