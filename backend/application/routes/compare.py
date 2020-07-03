from typing import List

from fastapi import APIRouter
import pandas

from application.models.Algorithm import Algorithm

router = APIRouter()


@router.get("/algorithms", response_model=List[Algorithm])
def get_algorithms():
    """
    Loads and returns the available routing algorithms.
    :return: a list of the available algorithms.
    """
    algs_data = pandas.read_csv('./application/assets/algorithms.csv')

    algorithms = []
    for algorithm in algs_data.itertuples():
        algorithms.append(Algorithm.from_csv_tuple(algorithm))
    return algorithms
