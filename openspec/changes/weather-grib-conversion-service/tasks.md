## 1. Project Setup

- [x] 1.1 Create project structure: `app/` with `api/`, `services/`, `models/`, `core/` directories
- [x] 1.2 Create `requirements.txt` with fastapi, uvicorn, pygrib, geojson, pydantic, python-multipart
- [x] 1.3 Create `config.yaml` for baseDir, thread_pool_size, zlevel_thresholds
- [x] 1.4 Create `app/core/config.py` to load configuration

## 2. Domain Models (Pydantic)

- [x] 2.1 Create `WeatherConvertRequest` model with version, gribFile, weatherType, height, time, prefix fields
- [x] 2.2 Create `WeatherConvertResponse` model with filePath, message, success fields
- [x] 2.3 Create `WeatherType` enum (TURB, CONV, ICE) with FastAPI validation

## 3. GRIB Parser Implementation

- [x] 3.1 Create `GribParser` class with pygrib
- [x] 3.2 Implement `parse()` method to open GRIB file and extract messages
- [x] 3.3 Implement `filter_by_type()` for TURB/CONV/ICE filtering
- [x] 3.4 Implement `filter_by_height()` for FL (TURB) and pressure level (CONV/ICE)
- [x] 3.5 Implement `filter_by_time()` for time point filtering
- [x] 3.6 Implement `map_zlevel()` severity mapping (TURB: 1-5, ICE/CONV: 1-2)
- [x] 3.7 Ensure resource cleanup with context manager or try/finally

## 4. GeoJSON Converter

- [x] 4.1 Create `GeoJsonConverter` class
- [x] 4.2 Implement `to_feature_collection()` method returning GeoJSON dict
- [x] 4.3 Implement `create_line_string()` from grid data points
- [x] 4.4 Add ZLEVEL property to feature properties
- [x] 4.5 Implement sequential feature ID assignment (0 to n-1)

## 5. Weather Data Storage

- [x] 5.1 Create `WeatherStorage` class
- [x] 5.2 Implement `build_output_path()` with directory structure template
- [x] 5.3 Implement `save()` method with parent directory creation
- [x] 5.4 Implement `overwrite` support for existing files

## 6. REST API Endpoint

- [x] 6.1 Create `router.py` with `@router.post("/weather/convert")`
- [x] 6.2 Implement request validation with Pydantic
- [x] 6.3 Implement error handling (400 invalid, 404 file not found, 500 processing error)
- [x] 6.4 Coordinate GribParser, GeoJsonConverter, WeatherStorage services

## 7. Concurrency & Resource Management

- [x] 7.1 Configure `ThreadPoolExecutor` with configurable max_workers
- [x] 7.2 Use `run_in_executor()` for CPU-intensive GRIB parsing
- [x] 7.3 Implement graceful shutdown in lifespan context
- [x] 7.4 Add disk space check before writing (optional)

## 8. Logging

- [x] 8.1 Configure Python `logging` module with structured format
- [x] 8.2 Add request/response logging with parameters
- [x] 8.3 Add GRIB parsing start/complete logging
- [x] 8.4 Add error logging with exception traceback

## 9. Application Entry Point

- [x] 9.1 Create `app/main.py` with FastAPI app and lifespan
- [x] 9.2 Include router and configure OpenAPI docs
- [x] 9.3 Add health check endpoint `@app.get("/health")`

## 10. Testing

- [x] 10.1 Write unit test for `WeatherConvertRequest` validation
- [x] 10.2 Write unit test for `GribParser` filtering logic
- [x] 10.3 Write unit test for `GeoJsonConverter`
- [x] 10.4 Write unit test for `WeatherStorage` path building
- [ ] 10.5 Write integration test for full conversion flow (requires actual GRIB files)
