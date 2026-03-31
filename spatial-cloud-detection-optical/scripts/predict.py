import argparse
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import os
from omnicloudmask import predict_from_array

def main():
    parser = argparse.ArgumentParser(description="Cloud Detection Skill for Optical Remote Sensing (OmniCloudMask)")
    parser.add_argument("--input", required=True, help="Path to input 4-band image (GeoTIFF) or NetCDF (.nc)")
    parser.add_argument("--output_mask", required=True, help="Path to save the output mask (GeoTIFF)")
    parser.add_argument("--output_png", required=True, help="Path to save the overview image (PNG)")
    parser.add_argument("--band_r", type=int, default=3, help="1-indexed Red band (default: 3)")
    parser.add_argument("--band_g", type=int, default=2, help="1-indexed Green band (default: 2)")
    parser.add_argument("--band_b", type=int, default=1, help="1-indexed Blue band (default: 1)")
    parser.add_argument("--band_nir", type=int, default=4, help="1-indexed NIR band (default: 4)")
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(args.output_mask)), exist_ok=True)

    print(f"Loading input: {args.input}")
    
    with rasterio.open(args.input) as src:
        profile = src.profile
        # Read bands based on user input (1-indexed)
        try:
            r = src.read(args.band_r)
            g = src.read(args.band_g)
            b = src.read(args.band_b)
            nir = src.read(args.band_nir)
        except IndexError:
            # Fallback if band indices are invalid for this file
            print(f"Warning: Band indices {args.band_r, args.band_g, args.band_b, args.band_nir} not fully available. Using first 4 bands or available bands.")
            r = src.read(1)
            g = src.read(min(2, src.count))
            b = src.read(min(3, src.count))
            nir = src.read(min(4, src.count))
            
        src_nodata = src.nodata
        
    input_array = np.stack([r, g, nir], axis=0).astype(np.float32)
    print("Running OmniCloudMask prediction...")
    # Bypass patch-shifting bug with no_data_value=np.nan
    mask = predict_from_array(input_array, apply_no_data_mask=False, no_data_value=np.nan)
    
    # Apply NoData manually to cleaning the mask boundaries
    if src_nodata is not None:
        if np.isnan(src_nodata):
            valid_mask = ~np.isnan(r)
            mask[0][~valid_mask] = 0
            r = np.nan_to_num(r, nan=0)
            g = np.nan_to_num(g, nan=0)
            b = np.nan_to_num(b, nan=0)
        else:
            mask[0][r == src_nodata] = 0
    
    print(f"Saving mask to: {args.output_mask}")
    profile.update(count=1, dtype=rasterio.uint8, nodata=255)
    with rasterio.open(args.output_mask, 'w', **profile) as dst:
        dst.write(mask.astype(rasterio.uint8))
        
    # Calculate statistics
    total_pixels = mask[0].size
    thick_cloud_pixels = np.sum(mask[0] == 1)
    thin_cloud_pixels = np.sum(mask[0] == 2)
    shadow_pixels = np.sum(mask[0] == 3)
    
    thick_percent = thick_cloud_pixels / total_pixels * 100
    thin_percent = thin_cloud_pixels / total_pixels * 100
    shadow_percent = shadow_pixels / total_pixels * 100
    cloud_cover = thick_percent + thin_percent
    
    print("-" * 30)
    print(f"Analysis Results:")
    print(f"Total Cloud Cover: {cloud_cover:.2f}%")
    print(f"  - Thick Cloud:   {thick_percent:.2f}%")
    print(f"  - Thin Cloud:    {thin_percent:.2f}%")
    print(f"  - Cloud Shadow:  {shadow_percent:.2f}%")
    print("-" * 30)

    # Visualization: Side-by-Side Report
    rgb = np.stack([r, g, b], axis=-1).astype(np.float32)
    for i in range(3):
        band = rgb[:, :, i]
        valid = band[band > 0]
        if len(valid) > 0:
            p2, p98 = np.percentile(valid, (2, 98))
            rgb[:, :, i] = np.clip((band - p2) / (p98 - p2 + 1e-8), 0, 1)
        else:
            rgb[:, :, i] = 0.0

    overlay = np.zeros(mask.shape[1:] + (4,), dtype=np.float32)
    overlay[mask[0] == 1] = [1.0, 1.0, 0.0, 0.6] # Thick: Yellow
    overlay[mask[0] == 2] = [0.0, 1.0, 1.0, 0.6] # Thin: Cyan
    overlay[mask[0] == 3] = [0.0, 0.0, 0.0, 0.6] # Shadow: Black

    fig, axes = plt.subplots(1, 2, figsize=(16, 9))
    
    # Left: Original RGB
    axes[0].imshow(rgb)
    axes[0].set_title("Original Image (RGB Overstretch)")
    axes[0].axis('off')
    
    # Right: RGB + Mask Overlay
    axes[1].imshow(rgb)
    axes[1].imshow(overlay)
    axes[1].set_title("Detection Result (Overlay)")
    axes[1].axis('off')
    
    stats_text = (f"Total Cloud: {cloud_cover:.2f}%\n"
                  f"Thick Cloud: {thick_percent:.2f}%\n"
                  f"Thin Cloud: {thin_percent:.2f}%\n"
                  f"Cloud Shadow: {shadow_percent:.2f}%")
    
    plt.figtext(0.5, 0.02, stats_text, ha="center", fontsize=12, 
                bbox={"facecolor":"white", "alpha":0.8, "pad":5})
    
    plt.savefig(args.output_png, bbox_inches='tight', pad_inches=0.1, dpi=120)
    plt.close()
    print(f"Comparison report saved to: {args.output_png}")
    print("Process completed successfully.")

if __name__ == "__main__":
    main()
