from pydantic import BaseModel
from typing import List, Optional

from application.models.GeoJSON import FeatureCollection


class Step(BaseModel):
    type: str
    location: List[float]
    load: List[int]
    arrival: float
    duration: float
    distance: float
    job: Optional[int]
    service: Optional[int]


class Route(BaseModel):
    vehicle: int
    cost: float
    delivery: List[int]
    amount: List[int]
    pickup: List[int]
    service: int
    duration: float
    waiting_time: float
    distance: float
    steps: List[Step]


class ORSResult(BaseModel):
    geojson: FeatureCollection
