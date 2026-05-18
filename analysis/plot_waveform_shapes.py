#!/usr/bin/env python3
"""
Waveform Shape Diagnostics

Plots representative waveforms corresponding to the two peaks in the distribution
(one small ~50 mV pulse, one medium ~150 mV pulse, and one large ~330 mV pulse)
to inspect their shape, noise level, and baseline, and save the figure.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    f_800 = os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL', '260508_173743_13_Ch3.wfm')
    
    reader = WfmReader(f_800)
    t, volts = reader.read_data(baseline_restore=True)
    t_ns = t * 1e9
    
    amps_mV = np.abs(np.min(volts, axis=1)) * 1000.0
    
    # Find event indices
    idx_50 = np.where((amps_mV >= 48.0) & (amps_mV <= 52.0))[0]
    idx_150 = np.where((amps_mV >= 145.0) & (amps_mV <= 155.0))[0]
    idx_330 = np.where((amps_mV >= 320.0) & (amps_mV <= 340.0))[0]
    
    if len(idx_50) == 0 or len(idx_150) == 0 or len(idx_330) == 0:
        print("Could not find events in all three ranges.")
        return
        
    ev_50 = idx_50[0]
    ev_150 = idx_150[0]
    ev_330 = idx_330[0]
    
    print(f"Plotting event {ev_50} (Peak: {amps_mV[ev_50]:.1f} mV)")
    print(f"Plotting event {ev_150} (Peak: {amps_mV[ev_150]:.1f} mV)")
    print(f"Plotting event {ev_330} (Peak: {amps_mV[ev_330]:.1f} mV)")
    
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    
    axes[0].plot(t_ns, volts[ev_50] * 1000.0, color='blue', label=f'Event {ev_50} (Peak: {amps_mV[ev_50]:.1f} mV)')
    axes[0].set_ylabel("Amplitude (mV)")
    axes[0].grid(True, linestyle='--')
    axes[0].legend()
    axes[0].set_title("Small Pulse (~50 mV Peak)")
    
    axes[1].plot(t_ns, volts[ev_150] * 1000.0, color='green', label=f'Event {ev_150} (Peak: {amps_mV[ev_150]:.1f} mV)')
    axes[1].set_ylabel("Amplitude (mV)")
    axes[1].grid(True, linestyle='--')
    axes[1].legend()
    axes[1].set_title("Medium Pulse (~150 mV Peak)")
    
    axes[2].plot(t_ns, volts[ev_330] * 1000.0, color='crimson', label=f'Event {ev_330} (Peak: {amps_mV[ev_330]:.1f} mV)')
    axes[2].set_ylabel("Amplitude (mV)")
    axes[2].set_xlabel("Time (ns)")
    axes[2].grid(True, linestyle='--')
    axes[2].legend()
    axes[2].set_title("Large Pulse (~330 mV Peak)")
    
    plt.tight_layout()
    out_file = os.path.join(base_dir, 'results', 'physical', 'cylindrical', 'waveform_diagnostics.png')
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    plt.savefig(out_file, dpi=150)
    plt.close()
    print(f"Saved diagnostic plots to: {out_file}")

if __name__ == "__main__":
    main()
