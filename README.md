# Spatial Cloud Detection Optical
This project is a universal cloud and cloud-shadow detection toolkit for optical remote sensing imagery. It is designed to provide a unified, high-precision, and large-image-friendly batch analysis solution for multi-source optical imagery (such as Sentinel-2, Landsat, PlanetScope, Maxar, etc.).
## 🧠 Core Algorithm (Acknowledgment)
The core cloud detection algorithm of this project is built upon **[OmniCloudMask](https://github.com/DPIRD-DMA/OmniCloudMask/blob/main/README.md)**.
OmniCloudMask provides an extremely generalizable deep learning model that makes cross-sensor cloud detection possible.
This project builds strictly upon the original algorithm by adding engineering encapsulation, edge-case optimizations for large images, automated outputs, and visualization enhancements. We extend our deep gratitude to the original authors (DPIRD-DMA) for their outstanding open-source work!
## 🌟 Key Features
1. **Broad Sensor Support**
   - **Mainstream Satellites:** Natively supports Sentinel-2, Landsat 8/9, PlanetScope (3m resolution), and Maxar (sub-meter resolution).
   - **Universal Optical Support:** Supports most standard 4-band remote sensing imagery (Red, Green, Blue, NIR).
2. **Precise Multi-Class Categorization**
   - Accurately classifies pixels into: **Clear Land (0)**, **Thick Cloud (1)**, **Thin Cloud (2)**, and **Cloud Shadow (3)**.
3. **Enhanced Large Image and Edge Processing**
   - Fixed coordinate offset issues that occur during inference on the edges of large images or areas containing NoData, ensuring 100% full-image coverage.
   - Built-in automatic Z-score normalization, providing strong robustness against lighting interference.
4. **Convenient Visual Analysis**
   - Automatically generates intuitive PNG overviews, displaying the Cloud Cover percentage and layer overlay effects directly on the image.
## 🛠️ Requirements
Please ensure your environment has Python 3.8+ and the following dependencies installed:
```bash
# Core dependencies including omnicloudmask and necessary spatial processing libraries
pip install omnicloudmask rasterio matplotlib numpy netCDF4 torch
```
*(Note: The `requirements.txt` included in this repository lists the complete environment dependencies.)*
## 🚀 Usage
Navigate to the `scripts/` directory and run the detection directly from the command line using the `predict.py` script:
```bash
python predict.py \
  --input "your_image.tif" \
  --output_mask "mask_result.tif" \
  --output_png "overview.png"
```
### Key Parameters:
- `--input` (Required): Path to the input image, supports `.tif` or `.nc` formats.
- `--output_mask` (Required): Path to save the output cloud detection classification GeoTIFF mask.
- `--output_png` (Required): Path to save the output visualization overview rendering.
- `--band_r / --band_g / --band_b / --band_nir` (Optional): Specify the band indices in the image (1-indexed). Defaults are 3, 2, 1, 4 corresponding to the R, G, B, NIR bands respectively.
## 📂 Outputs
1. **Mask File (mask_result.tif)**
   - Single-channel GeoTIFF format with spatial geo-referencing.
   - Pixel values: `0` = Clear Land; `1` = Thick Cloud; `2` = Thin Cloud; `3` = Cloud Shadow.
2. **Visualization Overview (overview.png)**
   - The original RGB rendering overlaid with the cloud and shadow classification results:
     - **Yellow Translucent Area:** Thick Cloud
     - **Cyan Translucent Area:** Thin Cloud
     - **Black Translucent Area:** Cloud Shadow
## ⚠️ Notes & Advanced Usage
- **Automatic Resolution Adaptation:** For remote sensing images with a spatial resolution of 2 meters or higher, the algorithm automatically performs resampling in the background to match the optimal detection features of the trained model. No manual downsampling is required.
- **Coordinate System Consistency:** The output GeoTIFF mask will perfectly inherit and retain the coordinate system and projection information of the input `.tif` file (if the input is `.nc` data, it defaults to outputting an unprojected TIFF).
## 📄 License
Please follow the respective open-source agreements. The core algorithm remains under the open-source license of OmniCloudMask.
