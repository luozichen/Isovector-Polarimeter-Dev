#!/usr/bin/env python3
"""
Single Waveform Detailed Inspector

Loads a single waveform from 800V Det 1 Ch3, prints its raw digitized values,
baseline, and full time-series profile to see if the peak is being calculated correctly
and where the 50 mV vs. 320 mV values are physically coming from.
"""

import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader

def inspect_waveform(filepath, event_idx=0):
    print(f"\n==========================================")
    print(f"  INSPECTING EVENT {event_idx} IN FILE:")
    print(f"  {os.path.basename(filepath)}")
    print(f"==========================================")
    
    try:
        reader = WfmReader(filepath)
        t, volts = reader.read_data(baseline_restore=True)
        t_ns = t * 1e9
        
        # Get raw data without baseline restoration for comparison
        _, volts_raw = reader.read_data(baseline_restore=False)
        
        raw_waveform = volts_raw[event_idx]
        restored_waveform = volts[event_idx]
        
        print(f"Waveform Length (samples): {len(t)}")
        print(f"Volt Scale:                 {reader.volt_scale:.6f} V/LSB")
        print(f"Volt Offset:                {reader.volt_offset:.6f} V")
        print(f"Raw digital values (first 10 samples):")
        # Back-calculate the integer LSB code
        raw_codes = (raw_waveform - reader.volt_offset) / reader.volt_scale
        print(f"  Codes: {np.round(raw_codes[:10]).astype(int)}")
        print(f"  Volts: {raw_waveform[:10] * 1000.0} mV")
        
        print(f"\nAfter baseline restoration:")
        print(f"  Baseline offset subtracted: {np.mean(volts_raw[event_idx, :50]) * 1000.0:.2f} mV")
        print(f"  Restored values (first 10 samples): {restored_waveform[:10] * 1000.0} mV")
        
        # Find absolute minimum (pulse peak)
        min_idx = np.argmin(restored_waveform)
        min_v = restored_waveform[min_idx] * 1000.0
        print(f"\nRestored Pulse Peak (Min Volts):")
        print(f"  Peak Amplitude: {np.abs(min_v):.2f} mV")
        print(f"  Peak Index:     {min_idx} (Time: {t_ns[min_idx]:.2f} ns)")
        
        # Check if the minimum is at the very boundary (edge) of the window!
        print(f"\nEdge Check:")
        print(f"  Value at first sample: {restored_waveform[0] * 1000.0:.2f} mV")
        print(f"  Value at last sample:  {restored_waveform[-1] * 1000.0:.2f} mV")
        
    except Exception as e:
        print(f"  Error: {e}")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    f_800 = os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL', '260508_173743_13_Ch3.wfm')
    
    # Inspect a few different events to see what is going on
    inspect_waveform(f_800, 0)
    inspect_waveform(f_800, 1)
    inspect_waveform(f_800, 2)

if __name__ == "__main__":
    main()
