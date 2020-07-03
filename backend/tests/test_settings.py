from fastapi.testclient import TestClient
from application.main import app

client = TestClient(app)

# TODO: more tests


def test_get_input():
    response = client.get("/settings/input_variables")

    assert response.status_code == 200
    assert response.json() is not None
    assert response.json() != {}


def test_set_algorithm():
    response = client.post(url="/settings/default_algorithm", json={"algorithm": 0})

    assert response.status_code == 200
