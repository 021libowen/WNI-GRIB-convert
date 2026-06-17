import logging
import os
import multiprocessing
import asyncio
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Form

from app.core.config import get_settings
from app.models.weather import WeatherConvertResponse, WeatherType
from app.services.grib_parser import GribParser
from app.services.geojson_converter import GeoJsonConverter
from app.services.weather_storage import WeatherStorage

logger = logging.getLogger(__name__)

router = APIRouter()

# 使用spawn模式创建进程池，避免fork问题
mp_context = multiprocessing.get_context('spawn')
executor = ProcessPoolExecutor(max_workers=get_settings().thread_pool_size, mp_context=mp_context)


def do_convert(
    gribFile: str,
    weatherType: str,
    height: str,
    time: str,
    version: str
) -> WeatherConvertResponse:
    """执行GRIB转GeoJSON的同步函数（可提交到进程池）"""
    try:
        grib_parser = GribParser()
        converter = GeoJsonConverter()
        storage = WeatherStorage()

        parsed_data = grib_parser.parse(
            grib_file=gribFile,
            weather_type=WeatherType(weatherType),
            height=height,
            time_str=time
        )

        if not parsed_data:
            return WeatherConvertResponse(
                FilePath="",
                Message="No matching data found for the specified criteria",
                Success=False
            )

        geojson_content = converter.to_feature_collection(parsed_data, WeatherType(weatherType))

        date_str = datetime.now().strftime("%Y-%m-%d")

        output_path = storage.build_output_path(
            weather_type=weatherType,
            height=height,
            version=version,
            time_str=time,
            date_str=date_str
        )

        storage.save(geojson_content, output_path)

        logger.info(f"Conversion successful: {output_path}")

        return WeatherConvertResponse(
            FilePath=output_path,
            Message="Conversion completed",
            Success=True
        )

    except Exception as e:
        logger.error(f"Conversion error: {e}", exc_info=True)
        raise


@router.post("/weather/convert", response_model=WeatherConvertResponse)
async def convert_weather(
    version: str = Form(...),
    gribFile: str = Form(...),
    weatherType: str = Form(...),
    height: str = Form(...),
    time: str = Form(...),
    prefix: str = Form("1")
) -> WeatherConvertResponse:
    """
    Convert GRIB weather data to GeoJSON format.

    POST /weather/convert (form-data)
    """
    logger.info(f"Received conversion request: version={version}, gribFile={gribFile}, weatherType={weatherType}, height={height}, time={time}, prefix={prefix}")

    if not os.path.exists(gribFile):
        logger.warning(f"GRIB file not found: {gribFile}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GRIB file not found"
        )

    if weatherType not in ["TURB", "CONV", "ICE"]:
        logger.warning(f"Invalid weather type: {weatherType}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid weather type"
        )

    try:
        # 提交到进程池执行，实现真正并发
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            do_convert,
            gribFile, weatherType, height, time, version
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversion error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversion processing error: {str(e)}"
        )
