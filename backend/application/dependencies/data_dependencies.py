from typing import List

import pandas as pd
from fastapi import Body
from application.models.Vehicle import Vehicle

from application.models.Delivery import Delivery

from application.models.Depot import Depot

from application.models.Scenario import Scenario


def deliveries_param(deliveries: List[Delivery] = Body(None)) -> List[Delivery]:
    """
    Must be used as FastAPI Dependency injection.
    Checks the deleveries passed in the request and returns them if present.
    Else, deliveries are loaded from file and returned.
    :param deliveries: An optional list of deliveries.
    :return: A list of deliveries.
    """
    if not deliveries:
        deliveries = load_deliveries('./application/assets/deliveries.csv')
    return deliveries


def vehicles_param(vehicles: List[Vehicle] = Body(None)) -> List[Vehicle]:
    """
    Must be used as FastAPI Dependency injection.
    Checks the vehicles passed in the request and returns them if present.
    Else, vehicles are loaded from file and returned.
    :param vehicles: An optional list of vehicles.
    :return: A list of vehicles
    """
    if not vehicles:
        vehicles = load_vehicles('./application/assets/vehicles.csv')
    return vehicles


def scenario_param(scenario: Scenario = Body(None)) -> Scenario:
    """
    Must be used as FastAPI Dependency injection.
    Checks the scenario passed in the request and returns them if present.
    Else, the scenario is loaded from file and returned.
    :param scenario: An object with all information for a scenario.
    :return: A scenario object
    """
    if not scenario:
        scenario = Scenario.read_from_file('./application/assets/sample_scenario.txt')
    return scenario


def load_vehicles(file_path: str):
    """
    Parses the csv file to a list of vehicle models.
    :param file_path: the path to the csv file to be parsed.
    :return: List of vehicle models.
    """
    vehicles_data = pd.read_csv(
        file_path,
        index_col="ID"
    )
    vs = []
    for vehicle in vehicles_data.itertuples():
        vs.append(Vehicle.from_csv_tuple(vehicle))
    return vs


def load_deliveries(content: str) -> List[Delivery]:
    """
    Parses the csv file to a list of delivery models.
    :param content: the csv file to be parsed
    :return: List of delivery models
    """
    deliveries_data = pd.read_csv(
        content,
        index_col="ID"
    )
    dlvs = []
    for delivery in deliveries_data.itertuples():
        dlvs.append(Delivery.from_csv_tuple(delivery))
    return dlvs


def load_depots(file_path):
    """
    Parses the csv file to a list of depot models.
    :return: List of depots
    """
    depots_data = pd.read_csv(
        file_path,
        index_col="ID"
    )
    deps = []
    for depot in depots_data.itertuples():
        deps.append(Depot.from_csv_tuple(depot))
    return deps
