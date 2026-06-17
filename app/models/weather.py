from enum import Enum

from pydantic import BaseModel, Field


class WeatherType(str, Enum):
    TURB = "TURB"
    CONV = "CONV"
    ICE = "ICE"


class WeatherConvertRequest(BaseModel):
    version: str
    gribFile: str
    weatherType: WeatherType
    height: str
    time: str
    prefix: str = "1"


class WeatherConvertResponse(BaseModel):
    FilePath: str = ""
    Message: str = ""
    Success: bool = False
