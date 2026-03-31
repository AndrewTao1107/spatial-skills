---
name: cloud-detection-optical
description: "基于 OmniCloudMask 的通用光学遥感云检测，支持 Sentinel-2, Landsat, PlanetScope, Maxar 等。"
risk: low
source: community
date_added: "2026-03-19"
---

# ☁️ 通用光学遥感云检测 (Cloud Detection Optical)

本 Skill 基于 **OmniCloudMask** 算法，为多源光学遥感影像提供统一、高精度的云与云影检测方案。它具有极强的传感器泛化能力，能够自动适配从 0.5米（高分/Maxar）到 30米（Landsat）的分辨率。

---

## 🚀 核心特性

### 1. 广谱传感器支持
- **主流卫星**：原生支持 Sentinel-2, Landsat 8/9, PlanetScope (3m) 和 Maxar (亚米级)。
- **通用光学支持**：支持大多数标准 4 波段遥感影像（R, G, B, NIR）。

### 2. 多类型分类
- 将像素精确分类为：**清晰地表 (0)**、**厚云 (1)**、**薄云 (2)**、**云影 (3)**。

### 3. 稳健的大图处理
- 修复了原始算法在大尺寸影像边缘或包含 NoData 区域时的坐标偏移 bug，确保全图 100% 覆盖识别。
- 内置自动 Z-score 归一化，抗光照干扰能力强。

### 4. 可视化分析
- 自动生成 PNG 概览图，包含云量统计（Cloud Cover %）和图层叠加效果。

---

## 🛠️ 使用方法

### 1. 环境准备
确保已安装 `omnicloudmask` 及其依赖：
```bash
pip install omnicloudmask rasterio matplotlib numpy netCDF4 torch
```

### 2. 命令行调用
进入 `scripts/` 目录运行：
```bash
python predict.py \
  --input "your_image.tif" \
  --output_mask "mask.tif" \
  --output_png "overview.png"
```

### 3. 主要参数说明
- `--input` (必填): 输入影像路径 (`.tif` 或 `.nc`)。
- `--output_mask` (必填): 输出的 GeoTIFF 掩膜路径。
- `--output_png` (必填): 输出的可视化概览图路径。
- `--band_r/g/b/nir` (选填): 指定红、绿、蓝、近红外波段的索引（1-indexed，默认为 3, 2, 1, 4）。

---

## 📂 输出说明
- **mask.tif**: 单通道 GeoTIFF。值为 0-3。
- **overview.png**: RGB 渲染图叠加：
  - **黄色**: 厚云
  - **青色**: 薄云
  - **黑色**: 云影

---

## ⚠️ 注意事项
- **分辨率适配**：对于 2米及更高分的影像，算法会自动进行重采样以匹配最佳检测特征。
- **坐标系**：输出的 TIFF 掩膜将继承输入文件的坐标系信息（如果是 `.nc` 格式，则输出为无投影 TIFF）。
