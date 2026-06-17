import os
import sys
import multiprocessing

# PyInstaller打包后需要设置DLL搜索路径
# 必须在导入任何可能加载pygrib的模块之前设置
if getattr(sys, 'frozen', False):
    root = sys._MEIPASS
    os.environ["PATH"] = root + os.pathsep + os.environ["PATH"]
    os.environ["ECCODES_PREFIX"] = root
    os.environ["ECCODES_HOME"] = root
    os.environ["PYGRIB_DATADIR"] = root
    # Python 3.8+ 需要显式添加DLL搜索目录
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(root)

# PyInstaller打包多进程支持
if getattr(sys, 'frozen', False):
    multiprocessing.freeze_support()

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router, executor
from app.core.config import load_config, get_settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_config()
    logger.info(f"Application starting with settings: {get_settings()}")
    yield
    logger.info("Application shutting down...")
    executor.shutdown(wait=True)
    logger.info("Executor shutdown complete")


app = FastAPI(
    title="Weather GRIB Conversion Service",
    description="REST API for converting GRIB weather data to GeoJSON format",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
