# 气象GRIB数据转化服务 - 部署实施文档

## 目录
1. [方案一：打包为独立exe（推荐）](#方案一打包为独立exe推荐)
2. [方案二：传统Python环境部署](#方案二传统python环境部署)
3. [接口调用](#接口调用)
4. [验证测试](#验证测试)
5. [Windows服务配置](#windows服务配置)

---

# 方案一：打包为独立exe（推荐）

## 1.1 构建exe

### 前置条件
- Python 3.10 或 3.11 已安装（仅用于打包，打包后无需安装）
- pip 已安装
- 网络连接（下载依赖）

### 构建步骤

1. **下载项目源码**
   将项目文件夹放到合适位置，如 `D:\weatherService\`

2. **以管理员身份运行 PowerShell**

```powershell
cd D:\weatherService

# 运行打包脚本
.\build.bat
```

3. **等待构建完成**
   首次构建需要下载Python依赖包和编译，可能需要10-20分钟。

4. **构建产物**
   ```
   D:\weatherService\dist\WeatherService\
   ├── WeatherService.exe      # 主程序（双击运行）
   ├── config.yaml             # 配置文件
   └── _internal\               # 运行库（不要修改）
   ```

## 1.2 配置exe

编辑 `dist\WeatherService\config.yaml`：

```yaml
baseDir: "D:/weatherData"           # 输出目录
thread_pool_size: 4                 # 线程数

# ZLEVEL分级配置 - 使用区间定义
zlevel_ranges:
  TURB:                            # 颠簸 - 5级分级
    - [0.1, 0.18]                  # ZLEVEL 1
    - [0.18, 0.3]                  # ZLEVEL 2
    - [0.3, 0.45]                  # ZLEVEL 3
    - [0.45, 0.6]                  # ZLEVEL 4
    - [0.6, 999.0]                 # ZLEVEL 5
  ICE:                             # 积冰 - 2级分级
    - [0.2, 0.49]                  # ZLEVEL 1
    - [0.5, 999.0]                 # ZLEVEL 2
  CONV:                            # 积云 - 使用CAPE物理量
    - [100, 2500]                  # ZLEVEL 1 (100-2500 J/kg)
    - [2500, 999999]                # ZLEVEL 2 (>=2500 J/kg)
```

## 1.3 运行exe

**方式一：直接双击运行**
```powershell
cd D:\weatherService\dist\WeatherService
.\WeatherService.exe
```

**方式二：命令行运行**
```powershell
cd D:\weatherService\dist\WeatherService
start WeatherService.exe
```

看到以下日志表示启动成功：
```
2026-04-24 10:30:00 - __main__ - INFO - Base directory: D:\weatherService\dist\WeatherService
2026-04-24 10:30:00 - __main__ - INFO - Loaded configuration: baseDir=D:/weatherData
2026-04-24 10:30:00 - __main__ - INFO - Starting Weather GRIB Conversion Service...
2026-04-24 10:30:00 - __main__ - INFO - Server started in background thread
```

服务运行在 `http://localhost:8000`

## 1.4 常见问题

**Q: 打包失败？**
确保网络畅通，首次打包需要下载所有依赖。

**Q: 运行时提示找不到 eccodes？**
这表示 pygrib 依赖的 eccodes 库未正确打包。需要：
1. 安装 Anaconda/Miniconda
2. 运行 `conda install -c conda-forge eccodes-python pygrib`
3. 重新运行 `build.bat`

**Q: exe运行报错？**
查看控制台错误信息，可能是config.yaml路径问题。

---

# 方案二：传统Python环境部署

## 2.1 环境要求

### 硬件环境
| 项目 | 最低要求 | 推荐配置 |
|------|---------|---------|
| CPU | 2核 | 4核+ |
| 内存 | 4GB | 8GB+ |
| 磁盘 | 10GB可用 | 50GB+ SSD |
| 网络 | 100Mbps | 1Gbps |

### 软件环境
| 项目 | 版本要求 |
|------|---------|
| 操作系统 | Windows Server 2019 |
| Python | 3.10.x 或 3.11.x |
| eccodes | Windows二进制版本 |
| pygrib | 与eccodes兼容版本 |

---

## 2.2 Python环境安装

### 2.2.1 下载Python

1. 访问 Python官网下载页面: https://www.python.org/downloads/windows/
2. 下载 Python 3.10.11 或 3.11.5 Windows installer (64-bit)
3. 运行安装程序

### 2.2.2 安装Python

```powershell
# 运行安装程序，选择以下选项：
# [x] Install launcher for all users
# [x] Add Python to PATH
# [x] Precompile standard library

# 自定义安装路径（建议）
# Install for all users: D:\Python310
```

### 2.3 验证Python安装

```powershell
python --version
# 输出: Python 3.10.11 或 Python 3.11.5

pip --version
# 输出: pip 2x.x.x from D:\Python310\lib\site-packages
```

### 2.4 创建虚拟环境（推荐）

```powershell
# 进入项目目录
cd D:\claude\weatherConvert

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\activate

# 验证激活
python --version
```

---

## 3. 项目部署

### 3.1 下载项目文件

将项目文件复制到服务器，如：`D:\weatherService\`

```
D:\weatherService\
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── services/
│   └── main.py
├── tests/
├── config.yaml
├── requirements.txt
└── pytest.ini
```

### 3.2 安装依赖

```powershell
# 激活虚拟环境（如使用）
.\venv\Scripts\activate

# 升级pip
python -m pip install --upgrade pip

# 安装依赖（不含pygrib，pygrib需要单独安装）
pip install -r requirements.txt
```

**注意**: `pygrib` 依赖 `eccodes` C库，Windows环境需要额外配置：

### 3.3 安装eccodes（pygrib依赖）

#### 方法一：使用预编译的二进制文件

1. 下载 eccodes-windows-binaries:
   - 访问: https://github.com/pp-mo/eccodes-python/releases
   - 下载 `eccodes-python-windows-binaries-x.x.x.tar.gz`

2. 安装:
```powershell
pip install eccodes-python-windows-binaries
```

#### 方法二：使用conda（如果安装了Anaconda）

```powershell
conda install -c conda-forge eccodes-python pygrib
```

#### 方法三：使用预编译的wgrib2

如果pygrib安装困难，可以使用wgrib2作为备选方案修改代码。

### 3.4 验证pygrib安装

```powershell
python -c "import pygrib; print('pygrib version:', pygrib.__version__)"
```

---

## 4. 配置说明

### 4.1 配置文件结构

编辑 `config.yaml`:

```yaml
baseDir: "D:/weatherData"           # 输出文件根目录
thread_pool_size: 4                  # 线程池大小，根据CPU核数调整

zlevel_ranges:                       # ZLEVEL分级区间配置
  TURB:                              # 颠簸 - 5级分级
    - [0.1, 0.18]                    # ZLEVEL 1: 0.1-0.18
    - [0.18, 0.3]                    # ZLEVEL 2: 0.18-0.3
    - [0.3, 0.45]                    # ZLEVEL 3: 0.3-0.45
    - [0.45, 0.6]                    # ZLEVEL 4: 0.45-0.6
    - [0.6, 999.0]                   # ZLEVEL 5: >0.6
  ICE:                               # 积冰 - 2级分级
    - [0.2, 0.49]                    # ZLEVEL 1: 0.2-0.49
    - [0.5, 999.0]                   # ZLEVEL 2: >=0.5
  CONV:                              # 积云 - 使用CAPE物理量(J/kg)
    - [100, 2500]                    # ZLEVEL 1: 100-2500
    - [2500, 999999]                 # ZLEVEL 2: >=2500
```

### 4.2 配置项说明

| 配置项 | 说明 | 示例值 |
|--------|------|--------|
| baseDir | 输出文件根目录 | `D:/weatherData` |
| thread_pool_size | 并发处理线程数 | `4` (建议CPU核数) |
| zlevel_ranges.TURB | TURB分级区间(5级) | `[[0.1, 0.18], [0.18, 0.3], [0.3, 0.45], [0.45, 0.6], [0.6, 999.0]]` |
| zlevel_ranges.ICE | ICE分级区间(2级) | `[[0.2, 0.49], [0.5, 999.0]]` |
| zlevel_ranges.CONV | CONV分级区间(CAPE) | `[[100, 2500], [2500, 999999]]` |

### 4.3 ZLEVEL分级逻辑

- **TURB (颠簸)**: 5级分级
  - ZLEVEL 1: 0.1 ≤ 值 < 0.18
  - ZLEVEL 2: 0.18 ≤ 值 < 0.3
  - ZLEVEL 3: 0.3 ≤ 值 < 0.45
  - ZLEVEL 4: 0.45 ≤ 值 < 0.6
  - ZLEVEL 5: 值 ≥ 0.6
  - 注: 值 < 0.1 视为无效/无颠簸

- **ICE (积冰)**: 2级分级
  - ZLEVEL 1: 0.2 ≤ 值 < 0.5
  - ZLEVEL 2: 值 ≥ 0.5
  - 注: 值 < 0.2 视为无效/无积冰

- **CONV (积云)**: 使用CAPE物理量(J/kg)，2级分级
  - ZLEVEL 1: 100 ≤ 值 < 2500
  - ZLEVEL 2: 值 ≥ 2500
  - 注: 值 < 100 视为无效/无对流

---

## 5. 服务启动

### 5.1 开发测试模式

```powershell
# 进入项目目录
cd D:\weatherService

# 激活虚拟环境
.\venv\Scripts\activate

# 设置配置文件路径（可选）
$env:CONFIG_PATH = "D:\weatherService\config.yaml"

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5.2 生产运行模式

```powershell
# 进入项目目录
cd D:\weatherService

# 激活虚拟环境
.\venv\Scripts\activate

# 后台运行服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

### 5.3 日志输出

服务启动后，日志输出到控制台：

```
2026-04-24 10:30:00 - app.core.config - INFO - Application starting with settings:...
2026-04-24 10:30:00 - uvicorn - INFO - Started server process
2026-04-24 10:30:00 - uvicorn - INFO - Application startup complete
```

---

## 6. 接口调用

### 6.1 接口信息

| 项目 | 值 |
|------|-----|
| URL | `POST http://localhost:8000/weather/convert` |
| Content-Type | `application/json` |

### 6.2 请求参数

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| version | string | 是 | 版本号 | `V20260416180000` |
| gribFile | string | 是 | GRIB文件绝对路径 | `D:/weatherTestData/test.grib` |
| weatherType | string | 是 | 数据类型 | `TURB` / `CONV` / `ICE` |
| height | string | 是 | 高度层 | `FL100` / `850` |
| time | string | 是 | 时间点 | `2026-04-23 18:00:00` |
| prefix | string | 否 | 稠稀密度，默认`1` | `1` |

### 6.3 请求示例

**cURL:**
```bash
curl -X POST "http://localhost:8000/weather/convert" ^
  -H "Content-Type: application/json" ^
  -d "{
    \"version\": \"V20260423160000\",
    \"gribFile\": \"D:/weatherTestData/ASC_SCALE_ICE_CONV_20260423160000/ASC_CONV_20260423160000.grib\",
    \"weatherType\": \"CONV\",
    \"height\": \"300\",
    \"time\": \"2026-04-23 18:00:00\",
    \"prefix\": \"1\"
  }"
```

**PowerShell:**
```powershell
$body = @{
    version = "V20260423160000"
    gribFile = "D:/weatherTestData/ASC_SCALE_ICE_CONV_20260423160000/ASC_CONV_20260423160000.grib"
    weatherType = "CONV"
    height = "300"
    time = "2026-04-23 18:00:00"
    prefix = "1"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/weather/convert" ^
                  -Method Post ^
                  -Body $body ^
                  -ContentType "application/json"
```

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/weather/convert",
    json={
        "version": "V20260423160000",
        "gribFile": "D:/weatherTestData/ASC_SCALE_ICE_CONV_20260423160000/ASC_CONV_20260423160000.grib",
        "weatherType": "CONV",
        "height": "300",
        "time": "2026-04-23 18:00:00",
        "prefix": "1"
    }
)
print(response.json())
```

### 6.4 响应格式

**成功响应:**
```json
{
    "FilePath": "D:/weatherData/2026-04-24/CONV/300/V20260423160000/20260423180000/CONV_300_20260423180000.txt",
    "Message": "Conversion completed",
    "Success": true
}
```

**失败响应:**
```json
{
    "FilePath": "",
    "Message": "GRIB file not found",
    "Success": false
}
```

### 6.5 高度层参数说明

| 数据类型 | height格式 | 示例 | 说明 |
|----------|-----------|------|------|
| TURB | FL + 数值 | `FL100` | 百英尺高度，FL100=10000英尺 |
| CONV | 数值 | `850` | 气压层(hPa) |
| ICE | 数值 | `850` | 气压层(hPa) |

---

## 7. 验证测试

### 7.1 健康检查

```bash
curl http://localhost:8000/health
```

响应: `{"status":"healthy"}`

### 7.2 API文档

访问 Swagger UI: http://localhost:8000/docs

### 7.3 运行单元测试

```powershell
# 进入项目目录
cd D:\weatherService

# 激活虚拟环境
.\venv\Scripts\activate

# 安装测试依赖
pip install pytest

# 运行测试
pytest
```

### 7.4 输出文件格式验证

输出文件为GeoJSON格式，可使用以下方式验证：

```python
import json

with open("D:/weatherData/2026-04-24/TURB/FL100/V20260417000000/20260417030000/TURB_FL100_20260417030000.txt", "r") as f:
    data = json.load(f)

print(f"Features count: {len(data['features'])}")
print(f"Sample feature: {data['features'][0]}")
```

---

## 8. Windows服务配置

### 8.1 使用NSSM将服务注册为Windows服务

#### 8.1.1 下载NSSM

1. 下载地址: https://nssm.cc/download
2. 解压到 `D:\nssm\`

#### 8.1.2 注册服务

```powershell
# 管理员权限运行PowerShell
cd D:\nssm\win64

# 注册服务
.\nssm.exe install WeatherService "D:\weatherService\venv\Scripts\python.exe"

# 配置服务参数
.\nssm.exe set WeatherService AppDirectory "D:\weatherService"
.\nssm.exe set WeatherService AppParameters "-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"
.\nssm.exe set WeatherService AppEnvironment "CONFIG_PATH=D:\weatherService\config.yaml"

# 设置启动类型
.\nssm.exe set WeatherService Start SERVICE_AUTO_START

# 设置显示名称和描述
.\nssm.exe set WeatherService DisplayName "Weather GRIB Conversion Service"
.\nssm.exe set WeatherService Description "气象GRIB数据转化REST服务"
```

#### 8.1.3 服务管理命令

```powershell
# 启动服务
net start WeatherService

# 停止服务
net stop WeatherService

# 删除服务
sc delete WeatherService

# 查看服务状态
sc query WeatherService
```

### 8.2 使用Task Scheduler（备选方案）

```powershell
# 创建任务计划（每天早上8点启动）
$action = New-ScheduledTaskAction -Execute "D:\weatherService\venv\Scripts\python.exe" -Argument "-m uvicorn app.main:app --host 0.0.0.0 --port 8000" -WorkingDirectory "D:\weatherService"
$trigger = New-ScheduledTaskTrigger -Daily -At "08:00"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -TaskName "WeatherService" -Description "Weather GRIB Conversion Service"
```

---

## 附录

### A. 常见问题

**Q: pygrib导入失败？**
```
ImportError: No module named 'pygrib'
```
解决: `pip install pygrib` 或使用conda安装 `conda install -c conda-forge pygrib`

**Q: 服务启动报错 "eccodes library not found"？**
解决: 安装eccodes-windows-binaries: `pip install eccodes-python-windows-binaries`

**Q: 请求返回500错误？**
解决: 检查GRIB文件是否存在，路径格式是否正确（Windows路径使用正斜杠`/`）

**Q: 如何调整并发数？**
解决: 修改 `config.yaml` 中的 `thread_pool_size` 值，重启服务

### B. 目录结构说明

```
输出文件路径格式:
{baseDir}/
└── {yyyy-MM-dd}/           # 日期
    └── {weatherType}/      # TURB/CONV/ICE
        └── {height}/       # FL100/850
            └── {version}/  # V20260417000000
                └── {time}/ # 20260417030000
                    └── {weatherType}_{height}_{time}.txt  # 输出文件
```

### C. 日志级别配置

修改 `app/main.py` 中的日志配置：

```python
logging.basicConfig(
    level=logging.DEBUG,  # 改为DEBUG获取更多日志
    ...
)
```

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-04-24 | 初始版本 |
