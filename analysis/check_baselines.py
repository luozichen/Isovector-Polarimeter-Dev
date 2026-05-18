#!/usr/bin/env python3
"""
Baseline Stability Check

Inspects the baseline of individual frames (first 50 samples of each frame)
across multiple waveforms in a single run to see if the baseline is stable
from frame to frame, or if there is a severe frame-dependent baseline offset.
"""

import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader

def check_baselines(filepath):
    print(f"\nChecking file: {os.path.basename(filepath)}")
    try:
        # Load raw data without baseline restoration first
        reader = WfmReader(filepath)
        t, volts = reader.read_data(baseline_restore=False)
        
        # Calculate baseline for each frame individually
        baselines = np.mean(volts[:, :50], axis=1) * 1000.0 # in mV
        
        print(f"  Total frames: {volts.shape[0]}")
        print(f"  Mean baseline:   {np.mean(baselines):.2f} mV")
        print(f"  Median baseline: {np.median(baselines):.2f} mV")
        print(f"  Std baseline:    {np.std(baselines):.2f} mV")
        print(f"  Min baseline:    {np.min(baselines):.2f} mV")
        print(f"  Max baseline:    {np.max(baselines):.2f} mV")
        
        # Print first 10 baselines
        print(f"  First 10 individual frame baselines (mV):")
        print(f"    {baselines[:10]}")
        
    except Exception as e:
        print(f"  Error: {e}")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    f_800 = os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL', '260508_173743_13_Ch3.wfm')
    check_baselines(f_800)

if __name__ == "__main__":
    main()
