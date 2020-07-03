from pydantic import root_validator
from pydantic.main import BaseModel
from typing import List, Dict, Optional
import typing


class Geometry(BaseModel):
    type: str
    coordinates: typing.Union[List[float], List[List[float]], List[List[List[float]]]]


class Feature(BaseModel):
    type: str = 'Feature'
    geometry: Geometry
    properties: typing.Union[None, Dict]

    @root_validator(pre=True)
    def valid(cls, values):
        geometry = Geometry(type=values["geometry"]["type"], coordinates=values["geometry"]["coordinates"])
        return {'geometry': geometry, 'properties': values.get("properties", None), 'type': values["type"]}

    class Config:
        orm_mode = True


class FeatureCollection(BaseModel):
    type: str = 'FeatureCollection'
    crs: Optional[Dict]
    features: List[Feature]
