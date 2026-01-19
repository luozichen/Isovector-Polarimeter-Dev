#!/usr/bin/env python3
"""
Waveform Analysis Tool for Isovector Polarimeter Test Data
Author: Gemini Agent
Date: January 2026
Description:
    Reads Tektronix FastFrame CSV files from data directories.
    Extracts multiple frames (events) from stacked CSV data.
    Plots waveforms for each channel.
    Calculates basic statistics (e.g., peak amplitude).

Usage:
    python3 analysis/analyse_waveform.py [data_directory]
    e.g. python3 analysis/analyse_waveform.py data/run001
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import argparse
import glob

def read_tek_csv(filepath):
    """
    Reads a Tektronix CSV file with stacked frames.
    Returns:
        time (np.array): Time array for one frame (assuming constant).
        frames (np.array): 2D array of voltage data (NumFrames x RecordLength).
        metadata (dict): Dictionary of extracted metadata.
    """
    # 1. Parse Metadata from the first few lines
    metadata = {}
    with open(filepath, 'r') as f:
        # Read first line to get Record Length
        line1 = f.readline().split(',')
        if "Record Length" in line1[0]:
            metadata['Record Length'] = int(line1[1])
        
    if 'Record Length' not in metadata:
        raise ValueError(f"Could not find 'Record Length' in {filepath}")
    
    record_length = metadata['Record Length']
    
    # 2. Read Data Columns (Time: col 3, Volts: col 4) - 0-indexed
    # header=None because line 1 contains data too.
    df = pd.read_csv(filepath, header=None, usecols=[3, 4], names=['Time', 'Volts'])
    
    # 3. Reshape
    total_points = len(df)
    num_frames = total_points // record_length
    
    if total_points % record_length != 0:
        print(f"Warning: Total points ({total_points}) is not a multiple of Record Length ({record_length}). Data might be truncated.")
    
    metadata['Num Frames'] = num_frames
    
    # Extract Time from the first frame
    time = df['Time'].values[:record_length]
    
    # Extract Voltage and reshape
    volts = df['Volts'].values
    # Truncate if necessary
    volts = volts[:num_frames * record_length]
    frames = volts.reshape((num_frames, record_length))
    
    return time, frames, metadata

def process_run(run_dir, output_dir):
    """
    Process all channels in a run directory.
    """
    print(f"Processing run directory: {run_dir}")
    
    # Find CSV files
    csv_files = glob.glob(os.path.join(run_dir, "*_Ch*.csv"))
    if not csv_files:
        print(f"No CSV files found in {run_dir}")
        return

    # Group by prefix
    sets = {}
    for f in csv_files:
        basename = os.path.basename(f)
        if "_Ch" in basename:
            prefix = basename.split("_Ch")[0]
            if prefix not in sets:
                sets[prefix] = {}
            
            try:
                ch_str = basename.split("_Ch")[1].split(".")[0]
                ch = int(ch_str)
                sets[prefix][ch] = f
            except ValueError:
                print(f"Skipping file with unexpected name format: {basename}")
    
    if not sets:
        print("No valid file sets found.")
        return

    os.makedirs(output_dir, exist_ok=True)

    # Process each set
    for prefix, channels in sets.items():
        print(f"Analyzing Set: {prefix}")
        
        data_map = {} # ch -> (time, frames)
        num_events = 0
        
        sorted_chs = sorted(channels.keys())
        for ch in sorted_chs:
            print(f"  Loading Ch{ch}...")
            try:
                t, f_data, meta = read_tek_csv(channels[ch])
                data_map[ch] = (t, f_data)
                num_events = meta['Num Frames']
            except Exception as e:
                print(f"    Error loading Ch{ch}: {e}")
        
        if not data_map:
            continue
            
        print(f"  Found {num_events} events.")
        
        # Plotting
        # Plot all events (up to 20)
        events_to_plot = min(num_events, 20)
        fig, axes = plt.subplots(events_to_plot, 1, figsize=(10, 3 * events_to_plot), sharex=True)
        if events_to_plot == 1:
            axes = [axes]
            
        for i in range(events_to_plot):
            ax = axes[i]
            for ch in sorted_chs:
                if ch in data_map:
                    t, f_data = data_map[ch]
                    if i < len(f_data):
                        ax.plot(t * 1e9, f_data[i] * 1000, label=f"Ch{ch}")
            
            ax.set_ylabel("Amplitude (mV)")
            ax.set_title(f"Event {i+1}")
            ax.grid(True, alpha=0.3)
            if i == 0:
                ax.legend(loc='upper right')
        
        axes[-1].set_xlabel("Time (ns)")
        plt.tight_layout()
        
        out_plot = os.path.join(output_dir, f"{prefix}_waveforms.png")
        plt.savefig(out_plot)
        print(f"  Saved plot to {out_plot}")
        plt.close(fig)
        
        # Calculate Peak Amplitudes and save to CSV
        results = []
        for i in range(num_events):
            row = {'Event': i}
            for ch in sorted_chs:
                if ch in data_map:
                    _, f_data = data_map[ch]
                    if i < len(f_data):
                        v_min = np.min(f_data[i])
                        v_max = np.max(f_data[i])
                        row[f'Ch{ch}_Min_V'] = v_min
                        row[f'Ch{ch}_Max_V'] = v_max
                        row[f'Ch{ch}_Peak_V'] = max(abs(v_min), abs(v_max))
            results.append(row)
            
        df_res = pd.DataFrame(results)
        out_csv = os.path.join(output_dir, f"{prefix}_analysis.csv")
        df_res.to_csv(out_csv, index=False)
        print(f"  Saved analysis to {out_csv}")

def main():
    parser = argparse.ArgumentParser(description="Analyze Waveform CSVs")
    parser.add_argument("data_dir", nargs='?', default="data/run001", help="Directory containing CSV files")
    parser.add_argument("--output", "-o", default="results", help="Output directory")
    
    args = parser.parse_args()
    
    process_run(args.data_dir, args.output)

if __name__ == "__main__":
    main()