# 气象数据转化服务

## 项目概述
气象GRIB数据解析转化服务，替代原有服务。通过RESTful接口接收GRIB文件路径，解析并转换为GeoJSON格式数据，按高度、时间等维度存储。

核心功能：
- 解析GRIB气象数据文件（TURB颠簸、CONV积云、ICE积冰）
- 按高度层和时间点提取数据并转化为GeoJSON格式
- 返回转换后的文件路径

## 技术栈
- Java（需根据现有代码推断版本）
- GRIB数据解析库（如eccodes、wgrib2等）
- Spring Boot（RESTful接口）
- GeoJSON格式输出

## 构建与运行
（需根据代码确定）

## 项目结构
- `weatherGrib/` - 源GRIB数据文件目录
- `weatherData/` - 转化后的GeoJSON数据输出目录
- `openspec/` - OpenSpec变更管理配置

## 注意事项
- 输出GeoJSON的ZLEVEL字段：TURB为1-5级，ICE为1-2级，CONV为1-2级
- 需要考虑多线程并发、资源释放、CPU占用
- 需要完整的日志记录
- 现有weatherData目录下有已转化的样本数据可参考
