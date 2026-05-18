#!/usr/bin/env python3
"""
File-by-File Amplitude Diagnostic for Detector 1 at 800V

Inspects the amplitude distribution of Detector 1 separately for each run
it featured in (1-3 Ch3, 5-1 Ch4, 1-6 Ch3) to see if one specific run or channel
is causing the anomalous 330 mV peak!
"""

import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader

def print_file_amps(filepath, channel_str, label):
    print(f"\n==========================================")
    print(f"  {label}")
    print(f"  File: {os.path.basename(filepath)} ({channel_str})")
    print(f"==========================================")
    try:
        reader = WfmReader(filepath)
        t, volts = reader.read_data(baseline_restore=True)
        amps_mV = np.abs(np.min(volts, axis=1)) * 1000.0
        
        # Filter out noise above 0.03 V positive excursion
        noise_mask = np.max(volts, axis=1) <= 0.03
        amps_filtered = amps_mV[noise_mask]
        # 10mV cut
        amps_filtered = amps_filtered[amps_filtered >= 10.0]
        
        print(f"  Total events (after 10mV cut): {len(amps_filtered)}")
        print(f"  Mean:   {np.mean(amps_filtered):.2f} mV")
        print(f"  Median: {np.median(amps_filtered):.2f} mV")
        print(f"  Min:    {np.min(amps_filtered):.2f} mV")
        print(f"  Max:    {np.max(amps_filtered):.2f} mV")
        
        # Print percentiles
        print(f"  Percentiles:")
        print(f"    25th: {np.percentile(amps_filtered, 25):.2f} mV")
        print(f"    50th: {np.percentile(amps_filtered, 50):.2f} mV")
        print(f"    75th: {np.percentile(amps_filtered, 75):.2f} mV")
        
    except Exception as e:
        print(f"  Error: {e}")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    dir_800 = os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL')
    
    # Detector 1 runs:
    run_13 = os.path.join(dir_800, '260508_173743_13_Ch3.wfm') # Det 1 is Top (Ch3)
    run_51 = os.path.join(dir_800, '260509_214220_51_Ch4.wfm') # Det 1 is Bot (Ch4)
    run_16 = os.path.join(dir_800, '260514_163701_16_Ch3.wfm') # Det 1 is Top (Ch3)
    
    print_file_amps(run_13, "Ch3", "Run 13 (Det 1 on Ch3)")
    print_file_amps(run_51, "Ch4", "Run 51 (Det 1 on Ch4)")
    print_file_amps(run_16, "Ch3", "Run 16 (Det 1 on Ch3)")

if __name__ == "__main__":
    main()
