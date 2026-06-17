## Why

现有气象数据转化服务需要替换，新服务需要支持通过RESTful接口调用，接收GRIB文件并返回解析转化后的GeoJSON数据，实现更灵活的气象数据访问能力。

## What Changes

- 新增RESTful接口服务，接收GRIB文件路径并返回转化后的GeoJSON文件路径
- 支持三种气象数据类型：TURB（颠簸）、CONV（积云）、ICE（积冰）
- 按高度层（FL百英尺或气压百帕）和时间点进行数据筛选
- 转化后的GeoJSON数据存储到可配置的baseDir目录
- 输出文件路径格式：`{baseDir}/{yyyy-MM-dd}/{weatherType}/{height}/{version}/{time}/{weatherType_height_time}.txt`
- ZLEVEL严重等级：TURB为1-5级，ICE为1-2级，CONV为1-2级
- 支持多线程并发调用
- 完善的资源释放和内存管理
- 完整的日志记录

## Capabilities

### New Capabilities
- `weather-grib-api`: GRIB数据转化REST接口，支持POST调用，参数包括version、gribFile、weatherType、height、time、prefix，返回文件路径、消息和成功标志
- `grib-parser`: GRIB气象数据解析器，解析TURB/CONV/ICE数据并提取指定高度和时间点的数据
- `geojson-converter`: GeoJSON格式转换器，将解析后的数据转换为GeoJSON FeatureCollection格式
- `weather-data-storage`: 气象数据存储模块，按目录结构存储转化后的GeoJSON文件

### Modified Capabilities
- （无）

## Impact

- 新增接口：`POST /weather/convert`
- 新增服务模块：GRIB解析器、GeoJSON转换器、数据存储
- 技术栈：**Python 3.10+ / FastAPI**（高并发、低延迟、开发效率高）
- 依赖：
  - `fastapi` + `uvicorn` - Web框架
  - `pygrib` 或 `cfgrib` + `eccodes` - GRIB解析
  - `geojson` - GeoJSON处理
  - `python-multipart` - 文件上传
- 配置：新增baseDir、并发线程数等配置项
