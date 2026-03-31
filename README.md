# 🌐 Spatial Skills
Welcome to **Spatial Skills**, a unified repository containing professional, production-grade geospatial toolkits and interactive web platforms designed for remote sensing analysis and renewable energy macro-siting.
This repository currently hosts two flagship modules:
1. **[Spatial Cloud Detection Optical](#1-spatial-cloud-detection-optical)**: A universal, deep-learning-based cloud and shadow detection toolkit for multi-source optical imagery.
2. **[Macro Resource Profiler Demo](#2-macro-resource-profiler-demo)**: An investment-grade, sub-second web platform for global wind and solar macro-siting analysis.
---
## 1. ☁️ Spatial Cloud Detection Optical
This project is a universal cloud and cloud-shadow detection toolkit for optical remote sensing imagery. It is designed to provide a unified, high-precision, and large-image-friendly batch analysis solution for multi-source optical imagery (such as Sentinel-2, Landsat, PlanetScope, Maxar, etc.).
### 🧠 Core Algorithm (Acknowledgment)
The core cloud detection algorithm of this project is built upon **OmniCloudMask**. OmniCloudMask provides an extremely generalizable deep learning model that makes cross-sensor cloud detection possible. This project builds strictly upon the original algorithm by adding engineering encapsulation, edge-case optimizations for large images, automated outputs, and visualization enhancements. *We extend our deep gratitude to the original authors (DPIRD-DMA) for their outstanding open-source work!*
### 🌟 Key Features
*   **Broad Sensor Support**:
    *   Mainstream Satellites: Natively supports Sentinel-2, Landsat 8/9, PlanetScope (3m resolution), and Maxar (sub-meter resolution).
    *   Universal Optical Support: Supports most standard 4-band remote sensing imagery (Red, Green, Blue, NIR).
*   **Precise Multi-Class Categorization**: Accurately classifies pixels into: Clear Land (0), Thick Cloud (1), Thin Cloud (2), and Cloud Shadow (3).
*   **Enhanced Large Image Processing**:
    *   Fixed coordinate offset issues that occur during inference on the edges of large images or areas containing NoData, ensuring 100% full-image coverage.
    *   Built-in automatic Z-score normalization for robust lighting interference mitigation.
*   **Convenient Visual Analysis**: Automatically generates intuitive PNG overviews demonstrating the layer overlay effects directly on the image.
### 🚀 Usage
Navigate to the `scripts/` directory and run the detection directly from the command line:
```bash
python predict.py \
  --input "your_image.tif" \
  --output_mask "mask_result.tif" \
  --output_png "overview.png"
```
*(See specific module directory for `--band_r`, `--band_g`, etc., parameter details).*
---
## 2. 🌍 Macro Resource Profiler Demo
An interactive, purely frontend + FastAPI backed web system leveraging high-resolution global datasets for rapid, macro-level wind and solar site assessment. It is specifically designed for investment-grade evaluations, providing sub-second geographical insights and theoretical yield calculations without heavy GIS desktop software.
### 🌟 Key Features
*   **Ultra-Fast Climate Reanalysis Integration**: Automatically pulls and aggregates up to `40,000` hourly time-series records per click based on the **Open-Meteo ERA5-Land (~9km)** dataset. Translates historical weather data into **100m hub-height wind speeds**, solar radiation fluxes, and cloud-cover penalties directly in memory.
*   **Micro-Terrain & Elevation Assessment**: Integrates **Copernicus GLO-30 (~30m)** global elevation data. It dynamically computes physical air density loss corrections and utilizes a proprietary 5-point array derivation to calculate surface slope—instantly triggering a `15°` steep slope red-line warning for civil engineering costs.
*   **LULC Compliance Overlay Clearance**: Features a live **ESA WorldCover 10m** (2020/2021) WMS spatial overlay with a transparent toggle. Equipped with an accurate bilingual legend to visually identify and bypass ecological redlines like forests, permanent water bodies, and basic farmlands.
*   **Professional Data Dashboards**: Renders three core analytical charts on the fly:
    1.  **16-Sector High-Frequency Wind Rose** (for determining predominant wind direction for turbine layout).
    2.  **Monthly Histogram Comparison** (Solar kWh/m² vs. Wind m/s).
    3.  **Intra-day 24-hour Demand/Yield Curve**.
### 🚀 Usage
This tool operates on a zero-config Vanilla JS + FastAPI architecture.
**1. Launch the Backend Engine:**
Navigate into the backend directory and spin up the Python compute engine (Ensure `fastapi`, `uvicorn`, and `requests` are installed).
```bash
cd resource-profiler-backend
uvicorn main:app --reload --port 8000
```
**2. Open the Interface:**
Simply double-click the `resource-profiler.html` file in the root of this module via any modern browser (Chrome/Edge). The system will automatically load the interactive MapLibre globe and establish a connection to your local backend.
---
### 📄 Global License & Notes
- Please follow the respective open-source agreements for individual sub-modules. The `Spatial Cloud Detection Optical` core algorithm remains under the open-source license of OmniCloudMask.
- The `Macro Resource Profiler` utilizes open datasets from Copernicus, ESA, and open-meteo APIs. Not for direct commercial mapping without respective upstream attribution.
