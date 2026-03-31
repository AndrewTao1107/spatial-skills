import argparse
import rasterio
from rasterio.windows import Window
import numpy as np
import os
import sys
import time
from tqdm import tqdm

try:
    import onnxruntime as ort
except ImportError:
    print("Error: onnxruntime not found")
    sys.exit(1)

def normalize_zscore(array):
    normalized = np.zeros_like(array, dtype=np.float32)
    for i in range(array.shape[0]):
        channel = array[i]
        mean = np.mean(channel)
        std = np.std(channel)
        normalized[i] = (channel - mean) / (std + 1e-8)
    return normalized

def main():
    parser = argparse.ArgumentParser(description="Tiled ONNX Inference for OmniCloudMask")
    parser.add_argument("--input", required=True)
    parser.add_argument("--model", default="omnicloudmask_core.onnx")
    parser.add_argument("--output_mask", required=True)
    parser.add_argument("--band_r", type=int, default=3)
    parser.add_argument("--band_g", type=int, default=2)
    parser.add_argument("--band_nir", type=int, default=4)
    parser.add_argument("--tile_size", type=int, default=512)
    parser.add_argument("--overlap", type=int, default=64)
    args = parser.parse_args()

    start_time = time.time()

    if not os.path.exists(args.model):
        print(f"Error: Model {args.model} not found")
        return

    print(f"Loading model: {args.model}")
    session = ort.InferenceSession(args.model)
    input_name = session.get_inputs()[0].name

    print(f"Opening input: {args.input}")
    with rasterio.open(args.input) as src:
        h, w = src.height, src.width
        profile = src.profile
        profile.update(count=1, dtype=rasterio.uint8, nodata=255)
        
        # Create output file
        with rasterio.open(args.output_mask, 'w', **profile) as dst:
            tile_size = args.tile_size
            overlap = args.overlap
            # Effective stride
            stride_h = tile_size - 2 * overlap
            stride_w = tile_size - 2 * overlap
            
            # Tiling strategy
            rows = range(0, h, stride_h)
            cols = range(0, w, stride_w)
            
            total_tiles = len(rows) * len(cols)
            print(f"Image dimensions: {w}x{h}")
            print(f"Processing {total_tiles} tiles...")
            
            pbar = tqdm(total=total_tiles)
            for y in rows:
                for x in cols:
                    # Define extraction window (with overlap)
                    win_y = max(0, y - overlap)
                    win_x = max(0, x - overlap)
                    win_h = min(h, y + stride_h + overlap) - win_y
                    win_w = min(w, x + stride_w + overlap) - win_x
                    
                    # Pad if smaller than tile_size (to keep constant input size for speed, though ONNX is dynamic)
                    # But for simplest logic, we just use the actual window and let ONNX handle it
                    window = Window(win_x, win_y, win_w, win_h)
                    
                    r = src.read(args.band_r, window=window)
                    g = src.read(args.band_g, window=window)
                    nir = src.read(args.band_nir, window=window)
                    
                    if r.size == 0:
                        pbar.update(1)
                        continue
                    
                    # Preprocess
                    input_data = np.stack([r, g, nir], axis=0).astype(np.float32)
                    input_data = normalize_zscore(input_data)
                    input_tensor = input_data[np.newaxis, ...]
                    
                    # Inference
                    outputs = session.run(None, {input_name: input_tensor})
                    mask = outputs[0][0]
                    if mask.ndim == 3: mask = mask[0]
                    
                    # Determine write area (non-overlapping part)
                    write_y = y
                    write_x = x
                    write_h = min(h, y + stride_h) - y
                    write_w = min(w, x + stride_w) - x
                    
                    if write_h > 0 and write_w > 0:
                        # Slice the mask result to match the write area
                        dy = write_y - win_y
                        dx = write_x - win_x
                        final_tile = mask[dy:dy+write_h, dx:dx+write_w]
                        dst.write(final_tile.astype(np.uint8), 1, window=Window(write_x, write_y, write_w, write_h))
                    
                    pbar.update(1)
            pbar.close()

    end_time = time.time()
    elapsed = end_time - start_time
    print(f"\n========================================")
    print(f"Task Completed Successfully!")
    print(f"Total Processing Time: {elapsed:.2f} seconds")
    print(f"Output saved to: {args.output_mask}")
    print(f"========================================")

if __name__ == "__main__":
    main()
