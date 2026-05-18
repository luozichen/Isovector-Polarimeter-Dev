#!/usr/bin/env python3
"""
Cylindrical Waveform Plotter - Representative Waveform Visualizer

Selects and plots representative clean waveforms (large-amplitude vs. medium-amplitude)
from the cylindrical detector cosmic ray runs at 800V, 850V, and 900V. The output plots
are grouped under the 'results/physical/cylindrical/' folder for clear visual thesis evidence.

Usage:
    python3 analysis/plot_cylindrical_waveforms.py
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import glob

# Add the parent directory to the path so we can import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader

def plot_waveforms_group(data_dir, output_dir, voltage_label):
    if not os.path.exists(data_dir):
        print(f"Directory {data_dir} not found. Skipping.")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    
    files = glob.glob(os.path.join(data_dir, '*.wfm'))
    if not files:
        print(f"No .wfm files found in {data_dir}.")
        return
        
    print(f"Processing waveforms for {voltage_label}...")
    
    large_pulses = []   # list of (time, volts, filename, event_idx)
    medium_pulses = []  # list of (time, volts, filename, event_idx)
    
    # Scan files to find representative waveforms
    for f in sorted(files):
        if len(large_pulses) >= 5 and len(medium_pulses) >= 5:
            break
            
        try:
            reader = WfmReader(f)
            t, volts = reader.read_data(baseline_restore=True)
            t_ns = t * 1e9
            
            for i in range(volts.shape[0]):
                waveform = volts[i]
                amp_mV = np.abs(np.min(waveform)) * 1000.0
                
                # Exclude electronic noise / positive spikes
                if np.max(waveform) > 0.03: 
                    continue
                    
                pulse_data = (t_ns, waveform * 1000.0, os.path.basename(f), i)
                
                # Categorize based on amplitude
                if amp_mV >= 200.0 and len(large_pulses) < 5:
                    large_pulses.append(pulse_data)
                elif 70.0 <= amp_mV < 180.0 and len(medium_pulses) < 5:
                    medium_pulses.append(pulse_data)
                    
        except Exception as e:
            pass
            
    # Fallback if not enough large pulses
    if len(large_pulses) == 0 or len(medium_pulses) == 0:
        print(f"  Warning: Could not find enough varied pulses for {voltage_label}. Skipping plot.")
        return
        
    num_plots = min(5, len(large_pulses), len(medium_pulses))
    
    # Draw Plot
    fig, axes = plt.subplots(num_plots, 2, figsize=(14, 2.2 * num_plots), sharex=True)
    fig.suptitle(f"Representative Cylindrical Waveforms ({voltage_label}) - Large vs. Medium Pulses", 
                 fontsize=15, fontweight='bold', y=0.98)
    
    # Left Column: Large Waveforms
    for idx in range(num_plots):
        t, v, fname, ev = large_pulses[idx]
        ax = axes[idx, 0]
        ax.plot(t, v, color='blue', alpha=0.8, lw=1.5, label='Large Signal')
        ax.axhline(0, color='black', linestyle=':', alpha=0.5)
        ax.set_ylabel("Amplitude (mV)")
        ax.grid(True, linestyle='--', alpha=0.5)
        if idx == 0:
            ax.set_title("Large Amplitudes (Higher Light Yield)", fontsize=11, fontweight='bold', color='blue')
        ax.legend(loc='upper right', fontsize=8)
        
    # Right Column: Medium Waveforms
    for idx in range(num_plots):
        t, v, fname, ev = medium_pulses[idx]
        ax = axes[idx, 1]
        ax.plot(t, v, color='green', alpha=0.8, lw=1.5, label='Medium Signal')
        ax.axhline(0, color='black', linestyle=':', alpha=0.5)
        ax.grid(True, linestyle='--', alpha=0.5)
        if idx == 0:
            ax.set_title("Medium Amplitudes (Standard Cosmic Rays)", fontsize=11, fontweight='bold', color='green')
        ax.legend(loc='upper right', fontsize=8)
        
    for i in range(num_plots):
        axes[i, 0].set_xlim([t_ns[0], t_ns[-1]])
        axes[i, 1].set_xlim([t_ns[0], t_ns[-1]])
        
    axes[-1, 0].set_xlabel("Time (ns)", fontsize=11)
    axes[-1, 1].set_xlabel("Time (ns)", fontsize=11)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    out_file = os.path.join(output_dir, f"waveforms_{voltage_label}.png")
    plt.savefig(out_file, dpi=150)
    plt.close()
    print(f"Saved representative waveforms plot to: {out_file}")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    output_dir = os.path.join(base_dir, 'results', 'physical', 'cylindrical')
    
    plot_waveforms_group(os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL'), output_dir, "800V")
    plot_waveforms_group(os.path.join(base_dir, 'data', 'LZC_850V_CYLINDRICAL'), output_dir, "850V")
    plot_waveforms_group(os.path.join(base_dir, 'data', 'LZC_900V_CYLINDRICAL'), output_dir, "900V")
    
    print("\nAll cylindrical waveform plots generated and grouped under results/physical/cylindrical/")

if __name__ == "__main__":
    main()
