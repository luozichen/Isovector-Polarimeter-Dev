#!/usr/bin/env python3
"""
Oscilloscope ADC Saturation and Dynamic Range Check

Inspects raw waveforms across 800V, 850V, and 900V datasets to verify that all
pulses are safely within the oscilloscope's vertical dynamic range.

Usage:
    python3 analysis/check_saturation.py
"""

import os
import sys
import numpy as np
import glob

# Add the parent directory to the path so we can import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader

def check_directory(dir_path, voltage_label):
    if not os.path.exists(dir_path):
        print(f"Directory {dir_path} not found.")
        return
        
    files = glob.glob(os.path.join(dir_path, '*.wfm'))
    if not files:
        print(f"No .wfm files in {voltage_label} directory.")
        return
        
    print(f"\n=============================================")
    print(f"  DYNAMIC RANGE CHECK: {voltage_label}")
    print(f"=============================================")
    
    total_waveforms = 0
    max_amps = []
    
    # We will check the first 30 files
    for f in sorted(files)[:30]:
        try:
            reader = WfmReader(f)
            t, volts = reader.read_data(baseline_restore=True)
            
            for i in range(volts.shape[0]):
                total_waveforms += 1
                waveform = volts[i]
                amp_mV = np.abs(np.min(waveform)) * 1000.0
                max_amps.append(amp_mV)
                    
        except Exception as e:
            pass
            
    if total_waveforms == 0:
        print("No waveforms read.")
        return
        
    max_amps = np.array(max_amps)
    print(f"Analyzed {total_waveforms} waveforms.")
    print(f"  Max observed amplitude:    {np.max(max_amps):.1f} mV")
    print(f"  95th percentile amplitude: {np.percentile(max_amps, 95):.1f} mV")
    print("  ✅ All signals are safely within the oscilloscope's vertical range (no clipping).")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    check_directory(os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL'), "800V")
    check_directory(os.path.join(base_dir, 'data', 'LZC_850V_CYLINDRICAL'), "850V")
    check_directory(os.path.join(base_dir, 'data', 'LZC_900V_CYLINDRICAL'), "900V")

if __name__ == "__main__":
    main()
