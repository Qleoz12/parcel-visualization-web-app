from pydantic import BaseModel


class Vehicle(BaseModel):
    id: int
    depot: int
    capacity: int

    @classmethod
    def from_csv_tuple(cls, data: tuple):
        """
        Parses a tuple originating from a csv file to a Vehicle object
        :param data: A tuple with the vehicle variables.
        :return: A Vehicle object
        """
        return cls(id=data.Index, depot=data.Depot, capacity=data.Capacity)