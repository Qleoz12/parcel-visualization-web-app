from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    ORS_API_KEY: str = ""
    ORS_URL: str = ""

    class Config:
        env_file = ".env"
