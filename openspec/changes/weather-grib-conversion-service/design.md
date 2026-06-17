## Context

现有气象数据转化服务基于旧架构，需要重新开发以支持RESTful接口调用。新服务需要接收GRIB格式气象数据文件路径，解析颠簸(TURB)、积云(CONV)、积冰(ICE)数据，按高度层和时间点筛选，转化为GeoJSON格式输出。

当前约束：
- 运行环境：**Windows Server 2019**（不支持容器部署）
- GRIB数据来源于气象站，包含多高度层、多时间点数据
- 输出GeoJSON需按ZLEVEL分级（TURB: 1-5, ICE/CONV: 1-2）
- 需要支持多线程并发调用
- 资源必须正确释放，避免内存泄漏

## Goals / Non-Goals

**Goals:**
- 提供RESTful接口接收GRIB文件并返回转化结果
- 正确解析GRIB数据并提取指定高度和时间点的数据
- 将数据转化为GeoJSON FeatureCollection格式
- 按目录结构存储输出文件
- 支持多线程并发，资源正确管理
- 完整的日志记录

**Non-Goals:**
- 不实现GRIB文件的写入/编辑功能
- 不实现前端界面
- 不实现数据持久化数据库

## Decisions

### 1. 技术栈：Python 3.10+ / FastAPI
**决定**：使用Python + FastAPI构建REST服务
**理由**：
- **开发效率高**：Python生态丰富，FastAPI几分钟即可搭建完整API
- **性能优异**：异步架构支持高并发，接近Node/Go性能
- **GRIB支持好**：pygrib/cfgrib库成熟，Python下eccodes绑定稳定
- **类型安全**：Pydantic提供自动请求验证和响应序列化
**替代方案**：Java Spring Boot
- 缺点：开发周期长，JVM资源占用大

### 2. GRIB解析方案
**决定**：使用pygrib库解析GRIB数据
**理由**：
- pygrib是Python下最成熟的GRIB解析库
- 基于eccodes C库，性能和功能都有保障
- 支持流式读取，内存可控
**替代方案**：cfgrib + xarray
- 缺点：对某些GRIB模板支持不如pygrib完整

### 3. GeoJSON输出格式
**决定**：使用FeatureCollection + LineString格式
**理由**：
- 现有weatherData目录中的数据格式已如此
- LineString适合表示网格化的气象数据区域
- GeoJSON是标准格式，便于后续GIS系统集成

### 4. ZLEVEL分级策略
**决定**：根据WNI数据严重程度映射到1-5级
- TURB: 原始数据值 → 5级分级
- ICE: 原始数据值 → 2级分级
- CONV: 原始数据值 → 2级分级
**理由**：符合气象行业标准和现有数据格式

### 5. 并发处理
**决定**：使用Python asyncio + ThreadPoolExecutor
**理由**：
- FastAPI原生支持async/await
- CPU密集型任务（GRIB解析）用线程池绕过GIL
- 便于控制并发数和优雅关闭

### 6. 目录结构
**决定**：`{baseDir}/{yyyy-MM-dd}/{weatherType}/{height}/{version}/{time}/`
**理由**：
- 按日期分类便于数据管理
- 嵌套目录结构避免单目录文件过多
- 路径信息完整可追溯

## Risks / Trade-offs

[风险] GRIB文件格式复杂，不同来源的GRIB可能有差异
→ 缓解：在开发初期充分测试多种GRIB样本文件，建立格式校验

[风险] 多线程并发时文件写入冲突
→ 缓解：每个请求写入独立文件路径，使用UUID或时间戳保证唯一性

[风险] 大文件GRIB解析内存占用高
→ 缓解：流式处理，使用完立即释放资源，限制单文件处理时间

[风险] 磁盘空间不足
→ 缓解：在处理前检查可用空间，空间不足时返回明确错误

## Migration Plan

1. 开发新服务模块（Windows环境直接运行Python），不影响现有服务
2. 在Windows 2019测试环境验证GRIB解析和GeoJSON转换正确性
3. 并发和资源管理压力测试
4. 使用Windows服务或Task Scheduler托管FastAPI进程
5. 全量切换，保留旧服务观察期
6. 旧服务下线

## Open Questions

1. ZLEVEL分级的阈值数值需与业务方确认
2. 现有weatherData中的数据格式是否需要兼容旧路径
3. 服务进程托管方式：Windows Service vs NSSM vs 手动运行
