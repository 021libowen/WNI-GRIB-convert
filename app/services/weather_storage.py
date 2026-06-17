import logging
import os
from pathlib import Path
from typing import Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class WeatherStorage:
    def __init__(self):
        self.settings = get_settings()

    def build_output_path(
        self,
        weather_type: str,
        height: str,
        version: str,
        time_str: str,
        date_str: Optional[str] = None
    ) -> str:
        """
        Build output file path following the directory structure:
        {baseDir}/{yyyy-MM-dd}/{weatherType}/{height}/{version}/{time}/{weatherType_height_time}.txt
        """
        if date_str is None:
            from datetime import datetime
            date_str = datetime.now().strftime("%Y-%m-%d")

        time_formatted = time_str.replace("-", "").replace(":", "").replace(" ", "")

        filename = f"{weather_type}_{height}_{time_formatted}.txt"

        parts = [
            self.settings.baseDir,
            date_str,
            weather_type,
            height,
            version,
            time_formatted,
            filename
        ]

        output_path = os.path.join(*parts)

        return output_path

    def save(
        self,
        content: str,
        output_path: str
    ) -> bool:
        """
        Save GeoJSON content to file.
        Creates parent directories if they don't exist.
        """
        try:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Saved GeoJSON to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving file {output_path}: {e}")
            raise

    def file_exists(self, path: str) -> bool:
        """Check if file exists."""
        return os.path.exists(path)
