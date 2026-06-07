from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_root_redirects_to_operational_ui() -> None:
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/ui/"


def test_operational_ui_is_served_by_fastapi() -> None:
    response = client.get("/ui/")

    assert response.status_code == 200
    assert "Enterprise Integration Agent" in response.text
    assert "Execute when policy allows" in response.text
    assert "Approval decision" in response.text
    assert "Audit timeline" in response.text
    assert "Montserrat" in response.text
    assert "Quick actions" in response.text


def test_operational_ui_assets_are_served() -> None:
    css_response = client.get("/ui/app.css")
    script_response = client.get("/ui/app.js")

    assert css_response.status_code == 200
    assert ".workspace" in css_response.text
    assert script_response.status_code == 200
    assert 'request("/agent/chat"' in script_response.text
    assert "/decision" in script_response.text
    assert "/execute" in script_response.text
    assert "/audit/" in script_response.text
    assert "addExecutionResult(data.simulation_result)" in script_response.text
