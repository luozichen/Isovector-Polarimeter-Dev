#!/usr/bin/env python3
"""
Coincidence Verification Diagnostic

Inspects if small pulses (~50 mV) on one channel (Ch3) have a coincident pulse
on the other channel (Ch4), or if they are single-channel triggers where the other
channel is completely quiet (flat baseline).
"""

import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader

def check_coincidence(filepath_ch3, filepath_ch4, event_idx):
    print(f"\n--- Checking Event {event_idx} ---")
    try:
        reader3 = WfmReader(filepath_ch3)
        reader4 = WfmReader(filepath_ch4)
        
        t3, volts3 = reader3.read_data(baseline_restore=True)
        t4, volts4 = reader4.read_data(baseline_restore=True)
        
        amp3_mV = np.abs(np.min(volts3[event_idx])) * 1000.0
        amp4_mV = np.abs(np.min(volts4[event_idx])) * 1000.0
        
        print(f"  Ch3 (Top) Peak Amp: {amp3_mV:.2f} mV")
        print(f"  Ch4 (Bot) Peak Amp: {amp4_mV:.2f} mV")
        
        # Check standard deviation of Ch4 to see if it is just flat noise
        # (excluding the region where a pulse would be, e.g. indices 250 to 350)
        baseline_indices = np.concatenate([np.arange(0, 200), np.arange(400, len(t3))])
        ch4_noise_std = np.std(volts4[event_idx, baseline_indices]) * 1000.0
        ch4_pulse_min = np.min(volts4[event_idx, 250:350]) * 1000.0
        
        print(f"  Ch4 baseline noise std:  {ch4_noise_std:.2f} mV")
        print(f"  Ch4 peak in pulse window: {np.abs(ch4_pulse_min):.2f} mV")
        
    except Exception as e:
        print(f"  Error: {e}")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    dir_800 = os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL')
    
    run_13_ch3 = os.path.join(dir_800, '260508_173743_13_Ch3.wfm')
    run_13_ch4 = os.path.join(dir_800, '260508_173743_13_Ch4.wfm')
    
    # Event 49 has Ch3 amp = 50.8 mV
    check_coincidence(run_13_ch3, run_13_ch4, 49)
    # Event 7 has Ch3 amp = 150.8 mV
    check_coincidence(run_13_ch3, run_13_ch4, 7)
    # Event 82 has Ch3 amp = 326.8 mV
    check_coincidence(run_13_ch3, run_13_ch4, 82)

if __name__ == "__main__":
    main()
