from pydantic import BaseModel
from typing import List

from application.models.Vehicle import Vehicle
from application.models.Depot import Depot
from application.models.Delivery import Delivery
from application.models.Scenario import Scenario


class Algorithm(BaseModel):
    key: int
    name: str
    default: int

    @classmethod
    def from_csv_tuple(cls, data: tuple):
        """
        Parses a tuple originating from a csv file to an Algorithm object
        :param data: A tuple with the algorithm data.
        :return: An Algorithm object
        """
        return cls(key=data.ID, name=data.Name, default=data.Default)


class AlgorithmVariables(BaseModel):
    id: int
    orders: int
    depotRadius: int

    @classmethod
    def from_csv_tuple(cls, data: tuple):
        """
        Parses a tuple originating from a csv file to an AlgortihmVariables object
        :param data: A tuple with the algorithm variables.
        :return: An AlgortihmVariables object
        """
        return cls(id=data.ID, orders=data.Orders, depotRadius=data.Depot_radius)


class AlgorithmDefaultInput(BaseModel):
    algorithm: int

    @classmethod
    def from_id(cls, a_id: int):
        """
        Parses a tuple originating from a csv file to an AlgortihmVariables object
        :param a_id: An integer indicating the algorithm id.
        :return: An AlgortihmDefaultInput object
        """
        return cls(algorithm=a_id)


class AlgorithmInput(BaseModel):
    input: List[AlgorithmVariables]
    vehicles: List[Vehicle]
    depots: List[Depot]
    deliveries: List[Delivery]
    scenario: Scenario
