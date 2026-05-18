#!/usr/bin/env python3
"""
Signed vs Unsigned 8-bit Integer (Wrapping) Diagnostic

Inspects if reading the raw Tektronix WFM#003 curves as signed 'int8'
instead of unsigned 'uint8' causes code wrapping and voltage distortions
(e.g., positive overshoots being wrapped into massive fake negative peaks).
"""

import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader

def check_wrapping(filepath):
    print(f"\n==========================================")
    print(f"  Checking Wrapping in: {os.path.basename(filepath)}")
    print(f"==========================================")
    try:
        reader = WfmReader(filepath)
        
        # Load raw bytes directly from the file to inspect the raw values
        with open(filepath, 'rb') as f:
            f.seek(reader.curve_offset)
            total_points = reader.num_frames * reader.time_size
            raw_bytes = np.fromfile(f, dtype=np.uint8, count=total_points)
            
        print(f"Raw bytes stats (treated as uint8):")
        print(f"  Min raw byte: {np.min(raw_bytes)}")
        print(f"  Max raw byte: {np.max(raw_bytes)}")
        print(f"  Number of bytes > 127: {np.sum(raw_bytes > 127)} (out of {total_points})")
        
        # Let's see what the values look like if there are bytes > 127
        if np.sum(raw_bytes > 127) > 0:
            indices = np.where(raw_bytes > 127)[0]
            print(f"  First 10 raw bytes > 127: {raw_bytes[indices[:10]]}")
            print(f"  First 10 raw bytes > 127 as signed int8: {raw_bytes[indices[:10]].astype(np.int8)}")
            
    except Exception as e:
        print(f"  Error: {e}")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # 800V
    f_800 = os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL', '260508_173743_13_Ch3.wfm')
    check_wrapping(f_800)
    
    # 900V
    f_900 = os.path.join(base_dir, 'data', 'LZC_900V_CYLINDRICAL', '260512_195730_15_Ch3.wfm')
    check_wrapping(f_900)

if __name__ == "__main__":
    main()
