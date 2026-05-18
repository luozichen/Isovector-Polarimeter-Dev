#!/usr/bin/env python3
"""
Max Amplitude Waveform Visualizer

Scans all cylindrical detector runs to find the single event with the absolute
maximum vertical amplitude (highest energy deposition) for 800V, 850V, and 900V.
Plots the Ch3 and Ch4 waveforms for these maximum events and saves the figures.

Usage:
    python3 analysis/plot_max_amplitude_waveforms.py
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import glob

# Add the parent directory to the path so we can import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader

def find_and_plot_max_event(data_dir, output_dir, voltage_label):
    if not os.path.exists(data_dir):
        print(f"Directory {data_dir} not found. Skipping.")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    
    files = glob.glob(os.path.join(data_dir, '*.wfm'))
    if not files:
        print(f"No .wfm files found in {data_dir}.")
        return
        
    # Group by prefix
    prefixes = set()
    for f in files:
        if '_Ch3.wfm' in f:
            prefixes.add(f.replace('_Ch3.wfm', ''))
        elif '_Ch4.wfm' in f:
            prefixes.add(f.replace('_Ch4.wfm', ''))
            
    print(f"Scanning all runs in {voltage_label} for absolute max amplitude event...")
    
    global_max_amp = 0.0
    best_event_data = None # (t, volts3, volts4, prefix, event_idx, amp3, amp4)
    
    for prefix in sorted(prefixes):
        file_ch3 = prefix + '_Ch3.wfm'
        file_ch4 = prefix + '_Ch4.wfm'
        
        if not os.path.exists(file_ch3) or not os.path.exists(file_ch4):
            continue
            
        try:
            reader3 = WfmReader(file_ch3)
            reader4 = WfmReader(file_ch4)
            
            t3, volts3 = reader3.read_data(baseline_restore=True)
            t4, volts4 = reader4.read_data(baseline_restore=True)
            t_ns = t3 * 1e9
            
            num_events = volts3.shape[0]
            for i in range(num_events):
                # Noise filters
                if np.max(volts3[i]) > 0.03 or np.max(volts4[i]) > 0.03:
                    continue
                    
                amp3_mV = np.abs(np.min(volts3[i])) * 1000.0
                amp4_mV = np.abs(np.min(volts4[i])) * 1000.0
                
                # Check if this is the largest pulse observed in either channel
                max_amp_here = max(amp3_mV, amp4_mV)
                if max_amp_here > global_max_amp:
                    global_max_amp = max_amp_here
                    best_event_data = (t_ns, volts3[i] * 1000.0, volts4[i] * 1000.0, 
                                       os.path.basename(prefix), i, amp3_mV, amp4_mV)
                                       
        except Exception as e:
            pass
            
    if best_event_data is None:
        print(f"No valid events found for {voltage_label}.")
        return
        
    t, v3, v4, fname, ev_idx, amp3, amp4 = best_event_data
    
    print(f"  Absolute Max Event Found!")
    print(f"    Run/File Prefix: {fname}")
    print(f"    Event Index:     {ev_idx}")
    print(f"    Ch3 Amplitude:   {amp3:.1f} mV")
    print(f"    Ch4 Amplitude:   {amp4:.1f} mV")
    print(f"    Global Max Peak: {global_max_amp:.1f} mV")
    
    # Plot Ch3 and Ch4 side-by-side or overlaid
    plt.figure(figsize=(10, 6))
    plt.plot(t, v3, color='blue', lw=2, label=f'Ch3 (Top Detector) - Peak: {amp3:.1f} mV')
    plt.plot(t, v4, color='crimson', lw=2, label=f'Ch4 (Bottom Detector) - Peak: {amp4:.1f} mV')
    plt.axhline(0, color='black', linestyle=':', alpha=0.5)
    
    # Draw limits
    min_observed = min(np.min(v3), np.min(v4))
    plt.ylim([min_observed * 1.15, max(np.max(v3), np.max(v4)) * 1.15])
    
    plt.title(f"Absolute Maximum Amplitude Event ({voltage_label})\nRun: {fname} | Event: {ev_idx}", 
              fontsize=13, fontweight='bold')
    plt.xlabel("Time (ns)", fontsize=11)
    plt.ylabel("Amplitude (mV)", fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='lower left', fontsize=10)
    
    out_file = os.path.join(output_dir, f"max_amplitude_{voltage_label}.png")
    plt.savefig(out_file, dpi=150)
    plt.close()
    print(f"Saved max amplitude plot to: {out_file}\n")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    output_dir = os.path.join(base_dir, 'results', 'physical', 'cylindrical')
    
    find_and_plot_max_event(os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL'), output_dir, "800V")
    find_and_plot_max_event(os.path.join(base_dir, 'data', 'LZC_850V_CYLINDRICAL'), output_dir, "850V")
    find_and_plot_max_event(os.path.join(base_dir, 'data', 'LZC_900V_CYLINDRICAL'), output_dir, "900V")
    
    print("All maximum amplitude waveform plots successfully generated!")

if __name__ == "__main__":
    main()
