import json

from fastapi import APIRouter

from application.models.GeoJSON import FeatureCollection

router = APIRouter()


@router.get("/geojson", response_model=FeatureCollection)
def get_geojson():
    """
    Returns the autonomous roads parsed from file.
    :return: The collection of roads that can be traversed autonomously, in GeoJSON format.
    """
    with open('./application/assets/nederlandse_grote_wegen.geojson') as f:
        return json.load(f)
