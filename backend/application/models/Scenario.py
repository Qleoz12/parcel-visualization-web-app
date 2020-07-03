from pydantic import BaseModel
from typing import List
import time
import os


class Parcel(BaseModel):
    request_origin: int
    request_destination: int
    request_time: int

    @classmethod
    def from_data(cls, org: int, dest: int, time: int):
        return cls(request_origin=org, request_destination=dest, request_time=time)

    def to_string(self):
        return str(self.request_origin)+" "+str(self.request_destination)+" "+str(self.request_time)+" "


class Scenario(BaseModel):
    vehicles: int
    capacity: int
    drivers: int
    time_active: int
    time_mode: int
    cost_vehicle: float
    cost_driver: float
    parcels: List[Parcel]

    @classmethod
    def read_from_file(cls, file_path: str):
        """
        Reads a file at the given location and parses it to a Scenario object
        :param file_path: The file path to the scenario file.
        :return: The Scenario object
        """
        variables = list()
        parcels = list()

        with open(file_path, 'r') as file:
            contents = file.read().split("\n\n")

            for v in contents[0].split("\n"):
                variables.append(v.split(" ")[0])

            for p in contents[1].split("\n"):
                if p != "":
                    params = p.split(" ")
                    parcels.append(Parcel.from_data(int(params[0]), int(params[1]), int(params[2])))

        return cls(vehicles=int(variables[0]), capacity=int(variables[1]), drivers=int(variables[2]),
                   time_active=int(variables[3]), time_mode=int(variables[4]), cost_vehicle=float(variables[5]),
                   cost_driver=float(variables[6]), parcels=parcels)

    def write_to_file(self):
        res = str(self.vehicles)+"\n"+str(self.capacity)+"\n"+str(self.drivers)+"\n"+str(self.time_active)+"\n"\
              +str(self.time_mode)+"\n"+str(self.cost_vehicle)+"\n"+str(self.cost_driver)+"\n"
        res += "\n"
        for p in self.parcels:
            res += p.to_string() + "\n"

        milliseconds = int(round(time.time() * 1000))
        file_name = "scenario_"+str(milliseconds)+".txt"
        path = "./application/assets/scenarios/"+file_name

        with open(path, "w") as out_file:
            out_file.writelines("./application/assets/scenarios/")

        files = os.listdir("./application/assets/scenarios/")
        # Using 50 as the maximum number of scenario files means supporting 50 simultaneous requests.
        # In practice, this will likely still support a much larger number of users.
        diff = len(files) - 50
        if diff > 0:
            for file in files[:diff]:
                os.remove("./application/assets/scenarios/"+file)

        return path
