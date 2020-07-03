from fastapi import APIRouter
import pandas as pd

from application.models.Algorithm import Algorithm, AlgorithmInput, AlgorithmVariables, AlgorithmDefaultInput
from application.models.Scenario import Scenario

from application.dependencies.data_dependencies import load_deliveries, load_depots, load_vehicles

router = APIRouter()


@router.get("/input_variables", response_model=AlgorithmInput)
def get_input():
    """
    Loads all algorithm input types: input variables, vehicles and depots.
    :return: Dict with lists of input types and values
    """
    obj = {
        "input": load_input_vars(),
        "vehicles": load_vehicles('./application/assets/vehicles.csv'),
        "depots": load_depots('./application/assets/depots.csv'),
        "deliveries": load_deliveries('./application/assets/deliveries.csv'),
        "scenario": Scenario.read_from_file('./application/assets/sample_scenario.txt')
    }
    return obj


@router.post("/default_algorithm")
def set_algorithm(alg: AlgorithmDefaultInput):
    """
    Updates the default algorithm.
    :param alg: The algorithm object to be set as new default
    """
    change_default(alg.algorithm)


def load_algorithms():
    """"
    Loads the algorithms data.
    :return: List of available algorithms
    """
    algorithms = []
    raw_algs = pd.read_csv(
        './application/assets/algorithms.csv'
    )
    for raw_algorithm in raw_algs.itertuples():
        algorithms.append(Algorithm.from_csv_tuple(raw_algorithm))
    return algorithms


def load_input_vars():
    """"
    Loads the data that is used for order generation.
    :return: List of randomizer input variables
    """
    input_vars = pd.read_csv(
        './application/assets/input_variables.csv'
    )
    input = []
    for var in input_vars.itertuples():
        input.append(AlgorithmVariables.from_csv_tuple(var))
    return input


def change_default(algorithm: int):
    """
    Updates the default attribute for algorithms on load.
    :param algorithm: The algorithm ID of the new default algorithm
    """
    algorithms = load_algorithms()

    result = []
    for alg in algorithms:
        if alg.key == algorithm:
            alg.default = 1
        else:
            alg.default = 0
        result.append([alg.key, alg.name, alg.default])

    df = pd.DataFrame(result, columns=['ID', 'Name', 'Default'])
    df.to_csv('./application/assets/algorithms.csv', index=False)
