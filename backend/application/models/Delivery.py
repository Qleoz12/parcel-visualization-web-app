from pydantic import BaseModel


class Delivery(BaseModel):
    id: int
    latitude: float
    longitude: float
    needed_amt: int

    @classmethod
    def from_csv_tuple(cls, data: tuple):
        """
        Parses a tuple originating from a csv file to a Delivery object
        :param data: A tuple with the delivery data.
        :return: A Delivery object
        """
        return cls(id=data.Index, longitude=data.Lon, latitude=data.Lat, needed_amt=data.Needed_Amount)

    @classmethod
    def from_raw_data(cls, pid, plat, plon, pna):
        """
        Creates a Delivery object using the specified parameters.
        :param pid: The delivery id
        :param plat: The delivery latitude
        :param plon: The delivery longitude
        :param pna: The delivery needed amount
        :return: A Delivery object
        """
        return cls(id=pid, longitude=plon, latitude=plat, needed_amt=pna)
