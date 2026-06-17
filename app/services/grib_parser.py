import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional

# PyInstaller打包后：设置DLL搜索路径并预加载eccodes
if getattr(sys, 'frozen', False):
    root = sys._MEIPASS
    os.environ["PATH"] = root + os.pathsep + os.environ.get("PATH", "")
    os.environ["ECCODES_PREFIX"] = root
    os.environ["ECCODES_HOME"] = root
    os.environ["PYGRIB_DATADIR"] = root
    # 预加载eccodes.dll及其依赖
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(root)
    import ctypes
    for dll in ["eccodes.dll", "eccodes_memfs.dll", "libpng16.dll", "jasper.dll", "aec.dll", "jpeg8.dll", "zlib.dll"]:
        dll_path = os.path.join(root, dll)
        if os.path.exists(dll_path):
            try:
                ctypes.CDLL(dll_path)
            except Exception:
                pass

try:
    import pygrib
    GRIB_AVAILABLE = True
except ImportError:
    GRIB_AVAILABLE = False

from app.core.config import get_settings
from app.models.weather import WeatherType

logger = logging.getLogger(__name__)


@dataclass
class ParsedGribData:
    """Parsed GRIB data with grid information."""
    lats: Any
    lons: Any
    values: Any
    zlevel: int
    level: Optional[int] = None


class GribParser:
    def __init__(self):
        self.settings = get_settings()

    def parse(
        self,
        grib_file: str,
        weather_type: WeatherType,
        height: str,
        time_str: str
    ) -> List[ParsedGribData]:
        """
        Parse GRIB file and extract data matching the specified filters.
        """
        if not GRIB_AVAILABLE:
            raise RuntimeError("pygrib library not available. Install: pip install pygrib")

        logger.info(f"Parsing GRIB file: {grib_file}, type: {weather_type}, height: {height}, time: {time_str}")

        parsed_data: List[ParsedGribData] = []
        grbs = None

        try:
            grbs = pygrib.open(grib_file)

            target_level = self._parse_height(height, weather_type)
            target_time = self._parse_time(time_str)

            for grb in grbs:
                if not self._filter_by_type(grb, weather_type, grib_file):
                    continue

                if not self._filter_by_height(grb, target_level, weather_type):
                    continue

                if not self._filter_by_time(grb, target_time):
                    continue

                lats, lons = grb.latlons()
                values = grb.values

                zlevel = self._map_zlevel(values, weather_type)

                parsed_data.append(ParsedGribData(
                    lats=lats,
                    lons=lons,
                    values=values,
                    zlevel=zlevel,
                    level=target_level
                ))

                logger.info(f"Extracted message: level={grb.level}, type={grb.typeOfLevel}")

        except Exception as e:
            logger.error(f"Error parsing GRIB file: {e}")
            raise
        finally:
            if grbs is not None:
                grbs.close()

        logger.info(f"Parsed {len(parsed_data)} messages from GRIB file")
        return parsed_data

    def _filter_by_type(self, grb: Any, weather_type: WeatherType, grib_file: str = None) -> bool:
        """Check if GRIB message matches weather type.

        ICE/CONV: 接口已传参，直接返回True（由API保证类型正确）
        TURB: 依赖shortName='turb'判断
        """
        if weather_type == WeatherType.TURB:
            type_of_level = getattr(grb, 'typeOfLevel', '')
            short_name = getattr(grb, 'shortName', '')
            return 'turb' in short_name.lower() or 'turbulence' in type_of_level.lower()

        # ICE/CONV由接口参数保证，不做GRIB内容过滤
        return True

    def _filter_by_height(self, grb: Any, target_level: int, weather_type: WeatherType) -> bool:
        """Check if GRIB message matches height level. Allows ±1 hPa tolerance."""
        level = getattr(grb, 'level', None)
        if level is None:
            return False
        return abs(level - target_level) <= 1

    def _filter_by_time(self, grb: Any, target_time: datetime) -> bool:
        """Check if GRIB message matches time point."""
        try:
            valid_time = grb.validDate
            if valid_time is None:
                return False
            return abs((valid_time - target_time).total_seconds()) < 3600
        except Exception:
            return False

    def _parse_height(self, height: str, weather_type: WeatherType) -> int:
        """Parse height string to level value (FL for TURB, pressure for others).

        Converts Flight Level to hPa for TURB type using ISA standard atmosphere formula.
        FL (Flight Level) = altitude in hundreds of feet
        """
        if weather_type == WeatherType.TURB and height.startswith('FL'):
            fl_value = int(height[2:])
            altitude_feet = fl_value * 100
            # ISA standard atmosphere formula: P = 1013.25 * (1 - 0.000006875 * alt)^5.255
            pressure_hpa = 1013.25 * pow(1 - 0.000006875 * altitude_feet, 5.255)
            # 四舍五入到最近的整数
            return int(round(pressure_hpa))
        return int(height)

    def _parse_time(self, time_str: str) -> datetime:
        """Parse time string to datetime."""
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

    def _map_zlevel(self, values: Any, weather_type: WeatherType) -> int:
        """
        Map raw severity values to ZLEVEL grades.

        TURB/ICE/CONV数据都是离散值，直接使用值本身作为ZLEVEL：
        - TURB: 1-5 → ZLEVEL 1-5，0为无效
        - ICE/CONV: 1-2 → ZLEVEL 1-2，0为无效
        """
        import numpy as np
        values_arr = np.array(values)
        # 排除0值（无效数据）
        non_zero = values_arr[values_arr > 0]
        if len(non_zero) == 0:
            return 1
        # 使用众数（出现最多的值）
        unique, counts = np.unique(non_zero, return_counts=True)
        zlevel = int(unique[np.argmax(counts)])
        # 确保在有效范围内
        if weather_type == WeatherType.TURB:
            return max(1, min(5, zlevel))
        else:  # ICE, CONV
            return max(1, min(2, zlevel))

    def _map_zlevel_grid(self, values: Any, weather_type: WeatherType) -> List[int]:
        """
        Map each grid cell to ZLEVEL grades.
        Returns a 2D array of ZLEVEL values.
        """
        ranges = self.settings.zlevel_ranges.get(weather_type.value, [])
        rows, cols = values.shape
        zlevel_grid = [[1 for _ in range(cols)] for _ in range(rows)]

        for i in range(rows):
            for j in range(cols):
                val = float(values[i, j])
                zlevel = 1
                for idx, range_def in enumerate(ranges):
                    min_val, max_val = range_def
                    if min_val <= val < max_val:
                        zlevel = idx + 1
                        break
                else:
                    # 大于最大区间
                    if len(ranges) > 0 and val >= ranges[-1][1]:
                        zlevel = len(ranges)
                zlevel_grid[i][j] = zlevel

        return zlevel_grid
