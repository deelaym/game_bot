from app.web.utils import json_response, error_json_response


def test_json_response():
    data = json_response({"test": "test"}, "ok")
    assert '{"status": "ok", "data": {"test": "test"}}'.encode() == data.body

def test_error_json_response():
    data = error_json_response(404,
                               "HTTPNotFound",
                               "HTTPNotFound",
                               {"error": "404 HTTPNotFound"}
                               )

    assert data.body == '{"status": "HTTPNotFound", "message": "HTTPNotFound", "data": {"error": "404 HTTPNotFound"}}'.encode()