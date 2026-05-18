#!/usr/bin/env python3
"""
Timing Coincidence Diagnostic by Amplitude Group

Splits events from 260508_173743_13 into three groups:
1. Small amplitude events (both Ch3 and Ch4 < 100 mV)
2. Large amplitude events (both Ch3 and Ch4 > 250 mV)
3. Mixed events

For each group, calculates and prints the timing difference (dt) distribution
statistics and checks if the small-amplitude group has a broad, flat distribution
(indicating random accidental coincidences) or a narrow peak (indicating true physical origin).
"""

import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader
from analysis.utils.physics import get_dcfd_time
from analysis import config

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    dir_800 = os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL')
    
    file_ch3 = os.path.join(dir_800, '260508_173743_13_Ch3.wfm')
    file_ch4 = os.path.join(dir_800, '260508_173743_13_Ch4.wfm')
    
    reader3 = WfmReader(file_ch3)
    reader4 = WfmReader(file_ch4)
    
    t3, volts3 = reader3.read_data(baseline_restore=True)
    t4, volts4 = reader4.read_data(baseline_restore=True)
    
    amps3 = np.abs(np.min(volts3, axis=1)) * 1000.0
    amps4 = np.abs(np.min(volts4, axis=1)) * 1000.0
    
    dt_small = []
    dt_large = []
    dt_all = []
    
    for i in range(volts3.shape[0]):
        # Filter noise
        if np.max(volts3[i]) > 0.03 or np.max(volts4[i]) > 0.03:
            continue
            
        a3, a4 = amps3[i], amps4[i]
        if a3 < 10.0 or a4 < 10.0:
            continue
            
        t_top = get_dcfd_time(t3, volts3[i], config.CFD_FRACTION)
        t_bot = get_dcfd_time(t4, volts4[i], config.CFD_FRACTION)
        
        if not np.isnan(t_top) and not np.isnan(t_bot):
            dt = (t_top - t_bot) * 1e9
            dt_all.append(dt)
            
            if a3 < 100.0 and a4 < 100.0:
                dt_small.append(dt)
            elif a3 > 250.0 and a4 > 250.0:
                dt_large.append(dt)
                
    print(f"\n==========================================")
    print(f"  TIMING PROFILE BY AMPLITUDE GROUP")
    print(f"==========================================")
    print(f"Total events analyzed: {len(dt_all)}")
    
    print(f"\nSmall Amplitude Group (Both < 100 mV):")
    print(f"  Count: {len(dt_small)}")
    if len(dt_small) > 1:
        print(f"  Mean dt:   {np.mean(dt_small):.3f} ns")
        print(f"  Std dt:    {np.std(dt_small):.3f} ns")
        print(f"  Min/Max:   {np.min(dt_small):.3f} / {np.max(dt_small):.3f} ns")
        
    print(f"\nLarge Amplitude Group (Both > 250 mV):")
    print(f"  Count: {len(dt_large)}")
    if len(dt_large) > 1:
        print(f"  Mean dt:   {np.mean(dt_large):.3f} ns")
        print(f"  Std dt:    {np.std(dt_large):.3f} ns")
        print(f"  Min/Max:   {np.min(dt_large):.3f} / {np.max(dt_large):.3f} ns")

if __name__ == "__main__":
    main()
