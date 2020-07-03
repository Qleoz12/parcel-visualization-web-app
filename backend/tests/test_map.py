from fastapi.testclient import TestClient

from application.main import app

client = TestClient(app)


def test_get_geojson():
    response = client.post(url="/map/geojson", params={"algorithm": 0}, json={})

    assert response.status_code == 200
    assert response.json() is not None
    assert response.json() != {}
