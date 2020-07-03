from fastapi.testclient import TestClient

from application.main import app

client = TestClient(app)

# TODO: more tests


def test_get_algorithms():
    response = client.get("/compare/algorithms")

    assert response.status_code == 200
    assert response.json() is not None
    assert response.json() != {}
