from pydantic import BaseModel


class Depot(BaseModel):
    id: int
    latitude: float
    longitude: float

    @classmethod
    def from_csv_tuple(cls, data: tuple):
        """
        Parses a tuple originating from a csv file to a Depot object
        :param data: A tuple with the depot variables.
        :return: A Depot object
        """
        return cls(id=data.Index, longitude=data.Lon, latitude=data.Lat)
