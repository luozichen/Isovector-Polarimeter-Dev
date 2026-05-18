#!/usr/bin/env python3
"""
900V Wide Amplitude Histogram Diagnostic

Prints bin counts for Detectors 1, 3, 5, 6 at 900V in the range 150 to 900 mV
to see why the fitting is failing for Detectors 1, 5, and 6.
"""

import os
import sys
import numpy as np
import glob

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_dir = os.path.join(base_dir, 'data', 'LZC_900V_CYLINDRICAL')
    
    files = glob.glob(os.path.join(data_dir, '*.wfm'))
    prefixes = set()
    for f in files:
        if '_Ch3.wfm' in f:
            prefixes.add(f.replace('_Ch3.wfm', ''))
        elif '_Ch4.wfm' in f:
            prefixes.add(f.replace('_Ch4.wfm', ''))
            
    detectors = [1, 3, 5, 6]
    det_amplitudes = {d: [] for d in detectors}
    
    for prefix in sorted(prefixes):
        file_ch3 = prefix + '_Ch3.wfm'
        file_ch4 = prefix + '_Ch4.wfm'
        if not os.path.exists(file_ch3) or not os.path.exists(file_ch4):
            continue
        pair_id = os.path.basename(prefix).split('_')[-1]
        if len(pair_id) != 2:
            continue
        det_top = int(pair_id[0])
        det_bot = int(pair_id[1])
        if det_top == 4 or det_bot == 4:
            continue
            
        try:
            reader3 = WfmReader(file_ch3)
            reader4 = WfmReader(file_ch4)
            _, volts3 = reader3.read_data(baseline_restore=True)
            _, volts4 = reader4.read_data(baseline_restore=True)
            
            for i in range(volts3.shape[0]):
                amp3_mV = np.abs(np.min(volts3[i])) * 1000.0
                amp4_mV = np.abs(np.min(volts4[i])) * 1000.0
                
                if det_top in det_amplitudes:
                    det_amplitudes[det_top].append(amp3_mV)
                if det_bot in det_amplitudes:
                    det_amplitudes[det_bot].append(amp4_mV)
        except Exception as e:
            pass
            
    print(f"\n==========================================")
    print(f"  900V WIDE SPECTRUM BIN COUNTS (150-900 mV)")
    print(f"==========================================")
    for d in detectors:
        amps = np.array(det_amplitudes[d])
        print(f"\nDetector {d} (Total events: {len(amps)}):")
        counts, bin_edges = np.histogram(amps, bins=15, range=(150, 900))
        for i in range(len(counts)):
            print(f"  {bin_edges[i]:.0f} - {bin_edges[i+1]:.0f} mV: {counts[i]}")

if __name__ == "__main__":
    main()
