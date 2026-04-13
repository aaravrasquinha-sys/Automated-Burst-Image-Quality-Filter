import cv2
import os
import shutil
import rawpy
import numpy as np
from src.filters import calculate_sharpness

# --- CONFIGURATION ---
INPUT_DIR = "data/input"
OUTPUT_DIR = "data/output"

# Create output folder or clean it if it exists
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR)

# Supported extensions (Standard + Canon Raw)
valid_exts = ('.jpg', '.jpeg', '.png', '.cr3', '.cr2')
files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(valid_exts)]

best_filename = None
best_score = -1.0 

print(f"🚀 Scanning {len(files)} wildlife photos to find the champion...")

for filename in files:
    path = os.path.join(INPUT_DIR, filename)
    current_img = None
    ext = filename.lower()

    try:
        # A. Handle RAW files via rawpy (Forced priority)
        if ext.endswith('.cr2') or ext.endswith('.cr3'):
            with rawpy.imread(path) as raw:
                # Develop RAW to RGB
                rgb = raw.postprocess(use_camera_wb=True, bright=1.0)
                # Convert RGB (rawpy) to BGR (OpenCV)
                current_img = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        
        # B. Handle Standard files via OpenCV
        else:
            current_img = cv2.imread(path)

        if current_img is None:
            continue

        # C. Run Analysis
        score = calculate_sharpness(current_img)
        print(f"📊 {filename}: Sharpness Score = {score:.2f}")

        # D. Keep track of the absolute winner
        if score > best_score:
            best_score = score
            best_filename = filename

    except Exception as e:
        print(f"⚠️ Error processing {filename}: {e}")

# --- FINAL OUTPUT ---
if best_filename:
    src_path = os.path.join(INPUT_DIR, best_filename)
    dst_path = os.path.join(OUTPUT_DIR, best_filename)
    shutil.copy(src_path, dst_path)
    
    print("\n" + "⭐" * 40)
    print(f"🏆 ULTIMATE WINNER: {best_filename}")
    print(f"📈 HIGHEST SCORE:  {best_score:.2f}")
    print(f"📂 SAVED TO:       {OUTPUT_DIR}")
    print("⭐" * 40)
else:
    print("❌ No valid images found in the input directory.")