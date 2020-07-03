from fastapi.testclient import TestClient

from application.main import app
from application.routes import orders

client = TestClient(app)


def test_get_random_orders():
    response = client.post(url="/orders/randomize", params={'orders': 5, 'depot_radius': 10000})

    assert response.status_code == 200


# def test_make_coordinate_list():
#    res = orders.make_coordinate_list(0, 3, 52.0114017, 4.3583900, 30000)
#    assert res.__len__() == 3
#    for item in res:
#        assert (item[1] > 51.7614017) and (item[1] < 52.2614017)
#        assert (item[2] > 4.1083900) and (item[2] < 4.6083900)
