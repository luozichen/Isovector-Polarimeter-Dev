#!/usr/bin/env python3
"""
Header Diagnostic for Tektronix WFM Files

Reads and prints the header parameters (version, scales, offsets, size) of WFM files
from 800V, 850V, and 900V directories to check for file version changes, header mismatches,
or vertical scaling anomalies.
"""

import os
import sys
import glob

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader

def diagnose_file(filepath):
    print(f"\nFile: {os.path.basename(filepath)}")
    try:
        reader = WfmReader(filepath)
        print(f"  WFM Version:        {repr(reader.version)}")
        print(f"  Num Frames:         {reader.num_frames}")
        print(f"  Time Size (samples):{reader.time_size}")
        print(f"  Time Scale:         {reader.time_scale:.4e} s/div or s/sample")
        print(f"  Time Offset:        {reader.time_offset:.4e} s")
        print(f"  Volt Scale:         {reader.volt_scale:.4e} V/digit")
        print(f"  Volt Offset:        {reader.volt_offset:.4e} V")
        print(f"  Data Format:        {reader.data_format}")
        print(f"  Bytes/Point:        {reader.bytes_per_point}")
    except Exception as e:
        print(f"  Error: {e}")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # 800V
    f_800 = glob.glob(os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL', '*.wfm'))
    if f_800:
        print("\n--- 800V Directory File ---")
        diagnose_file(sorted(f_800)[0])
        
    # 850V
    f_850 = glob.glob(os.path.join(base_dir, 'data', 'LZC_850V_CYLINDRICAL', '*.wfm'))
    if f_850:
        print("\n--- 850V Directory File ---")
        diagnose_file(sorted(f_850)[0])
        
    # 900V
    f_900 = glob.glob(os.path.join(base_dir, 'data', 'LZC_900V_CYLINDRICAL', '*.wfm'))
    if f_900:
        print("\n--- 900V Directory File ---")
        diagnose_file(sorted(f_900)[0])

if __name__ == "__main__":
    main()
