"""
Geant4 Landau Distribution Analysis Tool
Author: Zichen Luo
Date: January 2026
Description: Parses Geant4 Analysis CSV histograms and performs peak detection.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
import sys

def parse_geant4_histogram(filepath):
    """
    Parses a Geant4 Analysis CSV file (h1) to extract bin centers and counts.
    """
    with open(filepath, 'r') as f:
        content_str = f.read()
    
    lines = content_str.split('\n')
    nbins, xmin, xmax = 100, 0.0, 100.0
    data_start_line = 0

    for i, line in enumerate(lines):
        if line.startswith('#'):
            if 'axis fixed' in line:
                parts = line.split()
                nbins = int(parts[2])
                xmin = float(parts[3])
                xmax = float(parts[4])
        else:
            data_start_line = i
            break

    # Read using pandas, skipping the metadata header
    from io import StringIO
    df = pd.read_csv(StringIO(content_str), skiprows=data_start_line)
    counts = df['entries'].values

    # Handle underflow/overflow rows
    if len(counts) == nbins + 2:
        counts = counts[1:-1]

    bin_edges = np.linspace(xmin, xmax, nbins + 1)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    return bin_centers, counts, xmin, xmax

def main():
    parser = argparse.ArgumentParser(description="Analyse Geant4 CSV histograms.")
    parser.add_argument("files", nargs='+', help="Path to one or more CSV files.")
    parser.add_argument("--output", "-o", help="Save plot to file instead of showing.")
    args = parser.parse_args()

    plt.figure(figsize=(10, 6), dpi=120)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    valid_plots = 0
    for i, filepath in enumerate(args.files):
        if not os.path.exists(filepath):
            print(f"Warning: File {filepath} not found. Skipping.")
            continue

        filename = os.path.basename(filepath)
        print(f"Processing {filename}...")

        try:
            x, y, xmin, xmax = parse_geant4_histogram(filepath)
            
            # Physics Calculation: MPV (Most Probable Value)
            peak_energy = x[np.argmax(y)]
            
            label = f"{filename} (MPV: {peak_energy:.2f} MeV)"
            plt.step(x, y, where='mid', label=label, linewidth=1.5, color=colors[i % len(colors)])
            plt.fill_between(x, y, step='mid', alpha=0.15, color=colors[i % len(colors)])
            valid_plots += 1
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    if valid_plots > 0:
        plt.title("Detector Calibration: Cosmic Muon Energy Deposition", fontsize=14, pad=15)
        plt.xlabel("Energy Deposition [MeV]", fontsize=12)
        plt.ylabel("Counts", fontsize=12)
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.legend(frameon=True, fontsize=10)
        
        if args.output:
            plt.savefig(args.output)
            print(f"Plot saved to {args.output}")
        else:
            plt.show()
    else:
        print("No valid data to plot.")

if __name__ == "__main__":
    main()
