---
name: macro-resource-profiler-demo
description: "Macro Resource Profiler Demo (Bilingual): An investment-grade web system leveraging 9km ERA5-Land climate data, 30m DEM elevation, and 10m ESA WorldCover for rapid, macro-level wind/solar site assessment and terrain clipping. | 宏观新能源选址评估系统双语展示技能"
---

# Macro Resource Profiler Demo
# 新能源宏观选址评估系统

---

## 🌍 Introduction | 简介

**[EN]** This is a complete skill manual designed to quickly deploy and demonstrate the "Macro Resource Profiler Demo" to investors or clients. The system seamlessly integrates **Open-Meteo ERA5-Land (~9km climate reanalysis)**, **Copernicus GLO-30 (~30m global elevation)**, and **ESA WorldCover (~10m LULC WMS)**, achieving an all-in-one, sub-second exploratory assessment spanning from climate resource calculation to land compliance clearance.

**[CN]** 这是一个用于快速拉起并向资方展示“新能源宏观选址评估在线终端”的完整技能手册。本系统整合了 **Open-Meteo ERA5-Land (~9km 气象再分析库)**、**Copernicus GLO-30 (~30m 全球高程)** 以及 **ESA WorldCover (~10m 陆表覆盖 WMS)**，实现了从气候资源测算到土地合规排雷的一体化秒级勘探。

---

## 🎯 Core Features | 核心功能

**[EN]**
*   **Ultra-Fast Data Processing**: Automatically fetches up to `40,000` hourly time-series records for the target coordinates within the last 5 years. Computes **100m hub-height wind speed**, shortwave radiation, and cloud cover directly in memory.
*   **Elevation & Micro-Terrain**: Supports physical air density loss correction based on absolute elevation. Features a proprietary 5-point array derivation to calculate surface slope, triggering a `15°` steep slope red-line warning.
*   **Compliance Overlay & Clearance**: Instantly overlays the 10m historical remote sensing LULC (2020/2021) with one click. Uses an accurate bilingual legend to identify conflicts with forests, water bodies, and basic farmlands.
*   **Triple Data Dashboards**: Generates a 16-sector high-frequency wind rose, a monthly histogram comparison, and an intra-day 24-hour typical solar/wind consumption curve.

**[CN]**
*   **极速数据降维**：自动拉取目标点近五年最高 `40,000` 条逐小时间序列，直接在内存中汇算 **100米轮毂风速**、短波辐射与云量遮蔽率。
*   **高程与微地形测算**：支持物理绝对海拔空气密度折损修正；独创 5 点阵列求导测算地表 `15°` 陡坡红线警告。
*   **合规叠加排雷**：一键叠加调用 10m 级历史遥感时序 LULC（2020/2021），借助精准中英图例辨别林场、水系、基本农田冲突。
*   **三大数据看板**：生成 16 基准面高频风向玫瑰图、年内月度柱状差异图、日内 24 小时高频消纳曲线。

---

## 🚀 Operation Manual for Agents | 启动指引

**[EN]** Before demonstrating the system, the AI Agent (or the user) **MUST execute the following two steps**:
**[CN]** AI Agent （或用户本人）在进行系统演示前，**必须执行以下两步操作**：

### Step 1: Launch the FastAPI Backend | 步骤一：拉起 FastAPI 气象算法后端

**[EN]** The massive concurrent computations (thread pool concurrency, memory caching) are powered by Python.
- **Working Directory**: `./resource-profiler-backend/`
- **Execution Command**: 
  ```bash
  uvicorn main:app --reload --port 8000
  ```
- *Prerequisites*: Ensure `fastapi`, `uvicorn`, and `requests` are installed (`pip install fastapi uvicorn requests`). The service must remain active in the background.

**[CN]** 该系统的大规模并发计算（线程池并发、内存缓存器）由 Python 提供支持。
- **工作目录**: `./resource-profiler-backend/`
- **执行命令**: 
  ```bash
  uvicorn main:app --reload --port 8000
  ```
- *前置环境检查*: 若缺少依赖，请先行执行 `pip install fastapi uvicorn requests`。服务启动后必须保持后台挂起，前端方可通过 API 调用全网气象接口。

### Step 2: Load the Vanilla Frontend | 步骤二：加载纯净前端沙盘

**[EN]** Built with Vanilla JavaScript + CDNs for ultimate zero-config deployment. No Webpack or Vite overhead.
- **Target File**: `./resource-profiler.html`
- **Action**: Prompt the user to directly double-click and open this HTML file in any modern browser (Chrome/Edge).

**[CN]** 因为该平台追求极致“极连极用”，完全通过 Vanilla JavaScript + CDN 构建，没有任何 Webpack 或 Vite 的心智负担。
- **目标文件**: `./resource-profiler.html`
- **执行动作**: 提示用户直接在任意现代浏览器（Chrome/Edge）中**双击打开此 HTML 文件**即可。

---

## 💡 User Guide & Demo Flow | 最佳演示路径建议

**[EN]** When presenting to investors or clients, follow this interaction flow for maximum impact:
1. **Set the Scene**: Pan across the Esri Satellite basemap (which includes clear highway and boundary labels) to a remote plateau or coastline.
2. **Pin the Site**: Click on the location. The top-right panel automatically fills in the coordinates and instantly generates all macro-report cards and dynamic ECharts line graphs at the bottom.
3. **Highlight Rose & Warnings**: Point out the red `(⚠ Steep Slope)` tag if it appears. Reference the Wind Rose compass chart below to explain the predominant seasonal wind directions of the territory.
4. **The Ultimate Clearance Move**: Check the `Overlay ESA WorldCover (10m)` glass-morphism widget in the top right. As the 10-color legend emerges in the bottom left, demonstrate how the system instantly reveals if the proposed site is swallowed by vast greens (**Trees / Forest Redlines**) or pinks (**Cropland / Agricultural Land**), saving millions in potential regulatory pitfalls.

**[CN]** 在向资方或客户汇报时，建议遵循以下交互路径以达到最震撼的演示效果：
1. **先选定范围**：直接在左上角的 Esri 卫星底图（自带清晰边界公路标注）上漫游到人烟稀少的高原或海边。
2. **点定地坎**：点击该处地点，系统右上角将自动填入经纬度并在 1-2 秒内刷出所有宏观报告卡片和底部 ECharts 动态折线图。
3. **点亮玫瑰与警告**：留意指示板上是否弹出带有红色的 `(⚠陡坡)` 提示，并指向下方的风向玫瑰罗盘图，解释该地域的常年主导风季走向。
4. **终极排雷大招**：此时点击右上角的毛玻璃挂件 `☑ 叠加微观地表覆盖限制 (10m)`，随着左下角的 10色图例浮现，展示我们的目标地块是否被大面积的绿色（**Trees / 林木红线**）或者粉红（**Cropland / 农业用地**）完全吞噬。借此展示平台如何瞬间为百万级项目“止损防坑”。
