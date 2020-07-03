from fastapi import APIRouter, HTTPException
import pandas as pd
import osmnx as ox
import numpy as np
import concurrent.futures
from global_land_mask import globe
import threading
import requests
import json
from itertools import repeat
from typing import List

from application.models.Delivery import Delivery
from application.models.OrderFactory import OrderFactory
from application.routes import map as mp
from application.dependencies.data_dependencies import load_vehicles, load_depots

router = APIRouter()


@router.post("/randomize", response_model=List[Delivery])
def get_random_orders(orders: int, depot_radius: int):
    """
    Randomly generates new deliveries using the specified parameters.
    :param orders: The amount of orders that need to be generated.
    :param depot_radius: The radius of the area around a depot that each delivery should be in.
    :return: The list of generated deliveries.
    """
    depot_data = load_depots('./application/assets/depots.csv')
    vehicles = load_vehicles('./application/assets/vehicles.csv')

    # Delivery points can be generated too far from road segments, this will cause ORS to
    # throw an error. To prevent this from happening in the frontend, testruns are performed here.
    its = 0
    while True and its < 20:
        generated_orders = generator(depot_data, depot_radius, orders)

        try:
            res = mp.get_geojson(algorithm=0, deliveries=generated_orders, vehicles=vehicles)
            print(res)
            return generated_orders
        except Exception as e:
            print(e)
            its += 1

    raise HTTPException(status_code=508, detail="Order generation fails continuously.")


def random_coordinates(coordinates, depot_radius):
    """
    Make a list of random coordinates on land within certain bounds.
    :param coordinates: The coordinates of the center depot.
    :param depot_radius: The radius around the depot that sets the bounds of the random coordinates.
    :return: A list of random coordinates within certain bounds around a depot.
    """
    iterations = 0
    while iterations < 50:
        # By dividing the depot radius by constant 120000, the depot radius will be roughly maintained in coordinate
        # generation. This constant is valid in The Netherlands. In other regions in the world, especially with very
        # diverging latitude coordinates, the constant needs to be recalculated.
        radius_degree = depot_radius / 120000
        temp_lat = round(np.random.uniform(coordinates[0] - radius_degree, coordinates[0] + radius_degree), 7)
        temp_lon = round(np.random.uniform(coordinates[1] - radius_degree, coordinates[1] + radius_degree), 7)

        # Only return point if it is on land, otherwise try again.
        if globe.is_land(temp_lat, temp_lon):
            return temp_lat, temp_lon
        else:
            iterations += 1
    return coordinates[0], coordinates[1]


def get_single_order(index, coordinates, rad):
    """
    Get the nearest road to a pair of coordinates to use as delivery point.
    :param index: The identifier of a delivery.
    :param coordinates: The coordinates of the center depot.
    :param rad: The radius around the depot in which to generate orders.
    :return: A delivery point object.
    """
    thread_local = threading.local()
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.Session()
    session = thread_local.session
    iterations = 0

    while iterations < 50:
        lat, lon = random_coordinates(coordinates, rad)
        urli = "http://router.project-osrm.org/nearest/v1/car/" + str(lon) + "," + str(lat)
        print(urli)

        try:
            with session.get(urli) as response:
                string = response.content.decode('utf-8')
                data = json.loads(string)
                return Delivery.from_raw_data(index+1, data['waypoints'][0]['location'][1],
                                              data['waypoints'][0]['location'][0], 1)
        except Exception as e:
            print(e)
            iterations += 1
    return Delivery.from_raw_data(index+1, 90, 180, 1)


def order_method(dep, order_factory):
    """
    Generate orders around a single depot according to random point generation with validation.
    :param dep: The depot around which to generate orders.
    :param order_factory: An object containing the information needed to generate orders  around a depot
    :return: A list of random delivery points around a single given depot.
    """
    res_list = []

    if dep.id == order_factory.depot_number:
        order_count = order_factory.order_number - ((dep.id - 1) * order_factory.orders_per_depot)
    else:
        order_count = order_factory.orders_per_depot
    oinit = (dep.id - 1) * order_factory.orders_per_depot

    with concurrent.futures.ThreadPoolExecutor() as threader:
        temp_results = threader.map(get_single_order, range(oinit, oinit+order_count),
                                    repeat((dep.latitude, dep.longitude)), repeat(order_factory.depot_radius))

        for res_tuple in temp_results:
            res_list.append(res_tuple)

    return res_list


def generator(depot_data, depot_radius, order_number):
    """
    Generates a possible list of random delivery points.
    :param depot_data: A list of depot points to generate orders around.
    :param depot_radius: An integer indicating the radius around which to generate orders in km.
    :param order_number: The total number of orders to generate.
    :return: A list of random orders around the given depots.
    """
    res_orders = []
    order_factory = OrderFactory.make(int(order_number/len(depot_data)), len(depot_data), order_number, depot_radius)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(order_method, depot_data, repeat(order_factory))

        for res in results:
            res_orders += res

    return res_orders
