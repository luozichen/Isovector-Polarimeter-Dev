#!/usr/bin/env python3
"""
Raw Amplitude Diagnostic

Reads and prints the direct raw amplitude statistics for Detector 1
across 800V, 850V, and 900V to see if the raw voltages are truly decreasing
or if there is an index/channel mismatch.
"""

import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader

def print_raw_stats(filepath, label):
    print(f"\n--- {label} ---")
    print(f"File: {os.path.basename(filepath)}")
    try:
        reader = WfmReader(filepath)
        t, volts = reader.read_data(baseline_restore=True)
        
        # Calculate peak amplitude (min value since negative pulse, absolute value in mV)
        amps_mV = np.abs(np.min(volts, axis=1)) * 1000.0
        
        print(f"  Total Waveforms: {volts.shape[0]}")
        print(f"  Mean Peak Amp:   {np.mean(amps_mV):.2f} mV")
        print(f"  Median Peak Amp: {np.median(amps_mV):.2f} mV")
        print(f"  Max Peak Amp:    {np.max(amps_mV):.2f} mV")
        
        # Print a few raw values
        print(f"  First 5 peak amplitudes (mV): {amps_mV[:5]}")
    except Exception as e:
        print(f"  Error: {e}")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Detector 1 as Top (Ch3)
    f_800 = os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL', '260508_173743_13_Ch3.wfm')
    f_850 = os.path.join(base_dir, 'data', 'LZC_850V_CYLINDRICAL', '260510_192317_31_Ch4.wfm') # wait, 31 Ch4 is Det 1 (Bot)
    f_900 = os.path.join(base_dir, 'data', 'LZC_900V_CYLINDRICAL', '260512_195730_15_Ch3.wfm') # 15 Ch3 is Det 1 (Top)
    
    print_raw_stats(f_800, "800V (Det 1, Top/Ch3)")
    print_raw_stats(f_850, "850V (Det 1, Bot/Ch4)")
    print_raw_stats(f_900, "900V (Det 1, Top/Ch3)")

if __name__ == "__main__":
    main()
