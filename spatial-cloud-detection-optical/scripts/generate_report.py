import argparse
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import os

def main():
    parser = argparse.ArgumentParser(description="Generate Comparison Report for Cloud Detection")
    parser.add_argument("--image", required=True, help="Path to original GeoTIFF")
    parser.add_argument("--mask", required=True, help="Path to cloud mask GeoTIFF")
    parser.add_argument("--output", required=True, help="Path to save comparison PNG")
    parser.add_argument("--band_r", type=int, default=3)
    parser.add_argument("--band_g", type=int, default=2)
    parser.add_argument("--band_b", type=int, default=1)
    parser.add_argument("--max_size", type=int, default=2000, help="Max dimension for the report thumbnail")
    args = parser.parse_args()

    print(f"Loading image (subsampled): {args.image}")
    with rasterio.open(args.image) as src:
        # Calculate subsampling factor
        scale = max(src.height, src.width) / args.max_size
        out_shape = (int(src.height / scale), int(src.width / scale))
        
        r = src.read(args.band_r, out_shape=out_shape, resampling=rasterio.enums.Resampling.bilinear)
        g = src.read(args.band_g, out_shape=out_shape, resampling=rasterio.enums.Resampling.bilinear)
        b = src.read(args.band_b, out_shape=out_shape, resampling=rasterio.enums.Resampling.bilinear)
        
    print(f"Loading mask (subsampled): {args.mask}")
    with rasterio.open(args.mask) as src:
        mask = src.read(1, out_shape=out_shape, resampling=rasterio.enums.Resampling.nearest)

    # 1. Normalize RGB for display (2%-98% stretch)
    def stretch(band):
        valid = band[band > 0]
        if len(valid) > 0:
            p2, p98 = np.percentile(valid, (2, 98))
            return np.clip((band - p2) / (p98 - p2 + 1e-8), 0, 1)
        return np.zeros_like(band)

    rgb = np.stack([stretch(r), stretch(g), stretch(b)], axis=-1)

    # 2. Create Overlay
    # 1: Thick Yellow, 2: Thin Cyan, 3: Shadow Black
    overlay = np.zeros(mask.shape + (4,), dtype=np.float32)
    overlay[mask == 1] = [1.0, 1.0, 0.0, 0.6] 
    overlay[mask == 2] = [0.0, 1.0, 1.0, 0.6] 
    overlay[mask == 3] = [0.0, 0.0, 0.0, 0.6] 

    # 3. Plot
    print(f"Plotting report...")
    fig, axes = plt.subplots(1, 2, figsize=(20, 11), dpi=100)
    
    # Left: RGB
    axes[0].imshow(rgb)
    axes[0].set_title("Original Image (RGB Stretched)", fontsize=16)
    axes[0].axis('off')
    
    # Right: RGB + Mask
    axes[1].imshow(rgb)
    axes[1].imshow(overlay)
    axes[1].set_title("Cloud Detection Result (ONNX Model)", fontsize=16)
    axes[1].axis('off')

    # Add legend manually
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=[1.0, 1.0, 0.0, 0.6], edgecolor='none', label='Thick Cloud'),
        Patch(facecolor=[0.0, 1.0, 1.0, 0.6], edgecolor='none', label='Thin/Wispy Cloud'),
        Patch(facecolor=[0.0, 0.0, 0.0, 0.6], edgecolor='none', label='Cloud Shadow')
    ]
    axes[1].legend(handles=legend_elements, loc='upper right', fontsize=12)

    plt.tight_layout()
    plt.savefig(args.output, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    print(f"Success! Report saved to: {args.output}")

if __name__ == "__main__":
    main()
