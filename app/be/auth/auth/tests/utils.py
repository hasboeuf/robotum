def check_default_response(response):
    assert "code" in response.json
    assert "message" in response.json
