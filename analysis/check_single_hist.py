#!/usr/bin/env python3
"""
Single File Amplitude Histogram Diagnostic

Checks if the double-peak distribution is present in a single channel
of a single run (260508_173743_13_Ch3.wfm) or if it only appears when combining.
"""

import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader

def check_single_hist(filepath):
    print(f"\n==========================================")
    print(f"  Hist for: {os.path.basename(filepath)}")
    print(f"==========================================")
    try:
        reader = WfmReader(filepath)
        t, volts = reader.read_data(baseline_restore=True)
        amps_mV = np.abs(np.min(volts, axis=1)) * 1000.0
        
        # 10mV cut
        amps_filtered = amps_mV[amps_mV >= 10.0]
        
        # Create bins like the plotting script
        counts, bin_edges = np.histogram(amps_filtered, bins=20, range=(10, 450))
        
        print(f"Bin ranges and counts (10 to 450 mV):")
        for i in range(len(counts)):
            print(f"  {bin_edges[i]:.1f} - {bin_edges[i+1]:.1f} mV: {counts[i]}")
            
    except Exception as e:
        print(f"  Error: {e}")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    f_ch3 = os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL', '260508_173743_13_Ch3.wfm')
    check_single_hist(f_ch3)

if __name__ == "__main__":
    main()
