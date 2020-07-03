from pydantic import BaseModel


class OrderFactory(BaseModel):
    orders_per_depot: int
    depot_number: int
    order_number: int
    depot_radius: int

    @classmethod
    def make(cls, opd, dn, on, dr):
        """
        Creates a Delivery object using the specified parameters.
        :param opd: The number of orders per depot
        :param dn: The number of depots present
        :param on: The number of orders to make
        :param dr: The depot radius in metres
        :return: An OrderFactory object
        """
        return cls(orders_per_depot=opd, depot_number=dn, order_number=on, depot_radius=dr)
