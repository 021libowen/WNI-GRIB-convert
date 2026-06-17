import geojson
from geojson import Feature, FeatureCollection, LineString, Point
import numpy as np
import logging

from app.core.config import get_settings
from app.models.weather import WeatherType
from app.services.grib_parser import ParsedGribData

logger = logging.getLogger(__name__)


class GeoJsonConverter:
    def to_feature_collection(self, parsed_data: list[ParsedGribData], weather_type: WeatherType = None) -> str:
        """
        Convert parsed GRIB data to GeoJSON FeatureCollection.
        优先使用contour等值线提取，如果失败则用散点。
        """
        features = []
        feature_id = 0

        for data in parsed_data:
            cell_features = self._create_contour_features(data, feature_id, weather_type)
            if len(cell_features) == 0:
                # contour失败，用散点备用
                cell_features = self._create_scatter_features(data, feature_id, weather_type)
            features.extend(cell_features)
            feature_id += len(cell_features)

        collection = FeatureCollection(features)
        return geojson.dumps(collection, sort_keys=True)

    def _create_contour_features(self, data: ParsedGribData, start_id: int, weather_type: WeatherType) -> list:
        """
        使用matplotlib contour提取等值线，生成GeoJSON。
        对于离散数据(0,1,2)，用边界levels(0.5,1.5,2.5)来提取边界线。
        """
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        lats = np.array(data.lats)
        lons = np.array(data.lons)
        values = np.array(data.values)

        rows, cols = values.shape
        features = []

        try:
            # 降采样处理大网格数据
            sample_step = max(1, min(rows, cols) // 200)
            if sample_step > 1:
                lats_s = lats[::sample_step, ::sample_step]
                lons_s = lons[::sample_step, ::sample_step]
                values_s = values[::sample_step, ::sample_step]
            else:
                lats_s, lons_s, values_s = lats, lons, values

            # 获取所有唯一的非零值
            unique_values = np.unique(values_s[values_s > 0])
            if len(unique_values) == 0:
                return features

            # 判断是离散值还是连续值
            is_discrete = all(float(v) == int(v) for v in unique_values)

            if is_discrete and len(unique_values) > 1:
                # 离散值：用边界levels (0.5, 1.5, 2.5, ...)
                # contour会在边界处画线
                min_val = int(min(unique_values))
                max_val = int(max(unique_values))
                if weather_type == WeatherType.TURB:
                    levels = [1.5, 2.5, 3.5, 4.5, 5.5]
                else:
                    levels = [0.5, 1.5, 2.5]
            else:
                # 连续值或单一值：用原始值
                levels = unique_values

            # 使用contour提取等值线
            fig = None
            try:
                fig = plt.figure()
                contour = plt.contour(lons_s, lats_s, values_s, levels=levels)
            finally:
                plt.close(fig) if fig else plt.close()

            # 遍历每个等值线
            for i, segs in enumerate(contour.allsegs):
                boundary_level = contour.levels[i]

                # 边界level对应的ZLEVEL是 boundary_level + 0.5
                # 例如1.5的边界对应ZLEVEL=2.0
                if is_discrete:
                    zlevel = boundary_level + 0.5
                else:
                    zlevel = boundary_level

                if zlevel <= 0:
                    continue

                for seg in segs:
                    if len(seg) < 2:
                        continue

                    try:
                        coords = [[p[0], p[1]] for p in seg]
                        if len(coords) >= 2:
                            geometry = LineString(coordinates=coords)
                            properties = {"ZLEVEL": float(zlevel)}
                            feature = Feature(
                                id=start_id + len(features),
                                geometry=geometry,
                                properties=properties
                            )
                            features.append(feature)
                    except Exception as e:
                        logger.warning(f"Failed to create feature: {e}")
                        continue

        except Exception as e:
            logger.error(f"Contour extraction error: {e}")

        return features

    def _create_scatter_features(self, data: ParsedGribData, start_id: int, weather_type: WeatherType) -> list:
        """
        使用散点图方式生成GeoJSON（备用方案）。
        """
        lats = np.array(data.lats)
        lons = np.array(data.lons)
        values = np.array(data.values)

        features = []
        unique_values = np.unique(values[values > 0])

        for zlevel in unique_values:
            if zlevel <= 0:
                continue

            mask = values == zlevel
            for i in range(lats.shape[0]):
                for j in range(lats.shape[1]):
                    if mask[i, j]:
                        geometry = Point(coordinates=[float(lons[i, j]), float(lats[i, j])])
                        properties = {"ZLEVEL": float(zlevel)}
                        feature = Feature(
                            id=start_id + len(features),
                            geometry=geometry,
                            properties=properties
                        )
                        features.append(feature)

        return features

    def _calculate_zlevel(self, value: float, weather_type: WeatherType) -> int:
        """
        根据值和气象类型计算ZLEVEL等级。
        """
        if value <= 0:
            return 1

        zlevel = int(value)

        if weather_type == WeatherType.TURB:
            return max(1, min(5, zlevel))
        else:
            return max(1, min(2, zlevel))
