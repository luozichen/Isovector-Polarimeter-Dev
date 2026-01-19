#!/usr/bin/env python3
"""
Analysis for Run 002 (1000 events)
- Noise Rejection
- Landau Fitting
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import moyal
from scipy.optimize import curve_fit
import os
import glob
import sys

# Configuration
RUN_DIR = "data/run002_1000_data"
OUTPUT_DIR = "results"
NOISE_THRESHOLD_V = 0.03 # 30 mV threshold based on observed baseline stats
LANDAU_RANGE = (0.01, 0.4) # Range for fit (10mV to 400mV)
BINS = 50

def read_tek_csv(filepath):
    """
    Reads a Tektronix CSV file with stacked frames.
    """
    # 1. Parse Metadata
    metadata = {}
    with open(filepath, 'r') as f:
        line1 = f.readline().split(',')
        if "Record Length" in line1[0]:
            metadata['Record Length'] = int(line1[1])
            
    if 'Record Length' not in metadata:
        raise ValueError(f"Could not find 'Record Length' in {filepath}")
    
    record_length = metadata['Record Length']
    
    # 2. Read Data
    df = pd.read_csv(filepath, header=None, usecols=[3, 4], names=['Time', 'Volts'])
    
    # 3. Reshape
    total_points = len(df)
    num_frames = total_points // record_length
    
    metadata['Num Frames'] = num_frames
    
    time = df['Time'].values[:record_length]
    volts = df['Volts'].values[:num_frames * record_length]
    frames = volts.reshape((num_frames, record_length))
    
    return time, frames, metadata

def landau_fit_func(x, mpv, width, amp):
    return amp * moyal.pdf(x, loc=mpv, scale=width)

def analyze():
    print(f"Analyzing run directory: {RUN_DIR}")
    
    # Locate CSVs
    csv_files = glob.glob(os.path.join(RUN_DIR, "*_Ch*.csv"))
    if not csv_files:
        print("No CSV files found.")
        return

    # Group by prefix
    prefix = os.path.basename(csv_files[0]).split("_Ch")[0]
    print(f"Processing set: {prefix}")
    
    # Load Data
    data = {} # ch -> frames
    time = None
    num_events = 0
    
    for ch in range(1, 5):
        pattern = os.path.join(RUN_DIR, f"{prefix}_Ch{ch}.csv")
        files = glob.glob(pattern)
        if not files:
            print(f"Missing file for Ch{ch}")
            return
        
        print(f"  Loading Ch{ch}...")
        t, frames, meta = read_tek_csv(files[0])
        data[ch] = frames
        if time is None:
            time = t
        num_events = meta['Num Frames']

    print(f"Total Events: {num_events}")
    
    # Debug: Check baselines
    for ch in range(1, 5):
        max_vals = np.max(data[ch], axis=1)
        print(f"Ch{ch} Max V stats: Min={max_vals.min():.4f}, Max={max_vals.max():.4f}, Mean={max_vals.mean():.4f}")

    # Analysis Lists
    good_events = []
    noise_events = []
    
    # Peak Amplitudes (for good events)
    peaks = {1: [], 2: [], 3: [], 4: []}
    
    for i in range(num_events):
        is_noisy = False
        
        # Check Noise on all channels
        for ch in range(1, 5):
            # Check for positive excursion > threshold
            if np.max(data[ch][i]) > NOISE_THRESHOLD_V:
                is_noisy = True
                break
        
        if is_noisy:
            noise_events.append(i)
        else:
            good_events.append(i)
            # Calculate Peaks for this event
            for ch in range(1, 5):
                # Negative peak amplitude
                v_min = np.min(data[ch][i])
                peaks[ch].append(abs(v_min))

    print(f"Noise Rejection:")
    print(f"  Total: {num_events}")
    print(f"  Noisy: {len(noise_events)} ({len(noise_events)/num_events:.1%})")
    print(f"  Clean: {len(good_events)}")
    
    # Plot Noise Examples
    if noise_events:
        plot_noise_examples(time, data, noise_events[:5], prefix)
        
    # Plot Landau Fits
    plot_landau_fits(peaks, prefix)

def plot_noise_examples(time, data, event_indices, prefix):
    n = len(event_indices)
    fig, axes = plt.subplots(n, 1, figsize=(10, 3*n), sharex=True)
    if n == 1: axes = [axes]
    
    for i, idx in enumerate(event_indices):
        ax = axes[i]
        for ch in range(1, 5):
            ax.plot(time*1e9, data[ch][idx]*1000, label=f"Ch{ch}")
        
        ax.set_title(f"Rejected Event #{idx}")
        ax.set_ylabel("mV")
        ax.axhline(NOISE_THRESHOLD_V*1000, color='r', linestyle='--', label='Threshold')
        ax.grid(True, alpha=0.3)
        if i == 0: ax.legend(loc='upper right')
        
    axes[-1].set_xlabel("Time (ns)")
    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, f"{prefix}_noise_check.png")
    plt.savefig(out_path)
    print(f"Saved noise check: {out_path}")
    plt.close(fig)

def plot_landau_fits(peaks, prefix):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    results = []
    
    for i, ch in enumerate(range(1, 5)):
        ax = axes[i]
        vals = np.array(peaks[ch])
        
        # Filter range for plotting/fitting
        vals_fit = vals[(vals >= LANDAU_RANGE[0]) & (vals <= LANDAU_RANGE[1])]
        
        # Histogram
        y, x, _ = ax.hist(vals, bins=BINS, range=LANDAU_RANGE, 
                          density=False, histtype='stepfilled', alpha=0.4, label='Data')
        
        # Fit
        if len(vals_fit) > 50:
            bin_centers = (x[:-1] + x[1:]) / 2
            
            # Guesses
            mpv_guess = bin_centers[np.argmax(y)]
            width_guess = 0.01
            amp_guess = np.max(y) * 0.01
            
            try:
                popt, _ = curve_fit(landau_fit_func, bin_centers, y, 
                                    p0=[mpv_guess, width_guess, amp_guess], 
                                    bounds=([0, 0, 0], [1, 1, np.inf]))
                
                x_fine = np.linspace(LANDAU_RANGE[0], LANDAU_RANGE[1], 200)
                ax.plot(x_fine, landau_fit_func(x_fine, *popt), 'r-', lw=2, 
                        label=f'Fit\nMPV={popt[0]*1000:.1f} mV\nWidth={popt[1]*1000:.1f} mV')
            except Exception as e:
                print(f"Fit failed for Ch{ch}: {e}")
        
        ax.set_title(f"Channel {ch}")
        ax.set_xlabel("Amplitude (V)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, f"{prefix}_landau_fits.png")
    plt.savefig(out_path)
    print(f"Saved landau fits: {out_path}")
    plt.close(fig)

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    analyze()
