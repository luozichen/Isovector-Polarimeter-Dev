#!/usr/bin/env python3
"""
Geant4 Advanced Analysis Tool (v0200)
Author: Zichen Luo
Date: January 2026
Description: 
    Performs advanced physics analysis on Cosmic Ray data:
    1. XY Hit Maps (Beam Spot).
    2. Path Length vs Energy Deposition (dE/dx check).
    3. Angular Reconstruction (Zenith Angle).
"""

import uproot
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os

# Configuration
DEFAULT_INPUT_FILE = "simulation/v0200_coincidence/build/DET01_Cosmic_Result.root"
OUTPUT_FILE = "results/v02_advanced_physics.png"
TREE_NAME = "CosmicData"
THRESHOLD = 0.5 # MeV

def perform_analysis(filepath, output_path):
    print(f"Loading: {filepath}...")
    try:
        with uproot.open(filepath) as file:
            df = file[TREE_NAME].arrays(library="pd")
    except Exception as e:
        print(f"Error: {e}")
        return False

    # Filter 4-Fold Coincidence
    mask = (
        (df['Edep_Scin0'] > THRESHOLD) & 
        (df['Edep_Scin1'] > THRESHOLD) & 
        (df['Edep_Scin2'] > THRESHOLD) & 
        (df['Edep_Scin3'] > THRESHOLD)
    )
    df_c = df[mask].copy()
    print(f"Events: {len(df)} | Coincidences: {len(df_c)}")

    if len(df_c) == 0:
        print("No coincidence events found.")
        return False

    # --- Calculations ---

    # 1. Path Length in Scin0
    # L = sqrt(dx^2 + dy^2 + dz^2)
    dx = df_c['Scin0_OutX'] - df_c['Scin0_InX']
    dy = df_c['Scin0_OutY'] - df_c['Scin0_InY']
    dz = df_c['Scin0_OutZ'] - df_c['Scin0_InZ']
    df_c['PathLen0'] = np.sqrt(dx**2 + dy**2 + dz**2)

    # 2. Zenith Angle Reconstruction
    # Vector from Scin0_In to Scin3_In (Top to Bottom)
    # Note: Scin0 is at +Z, Scin3 is at -Z. Muons go DOWN (-Z).
    vec_x = df_c['Scin3_InX'] - df_c['Scin0_InX']
    vec_y = df_c['Scin3_InY'] - df_c['Scin0_InY']
    vec_z = df_c['Scin3_InZ'] - df_c['Scin0_InZ'] # Should be negative
    
    vec_r = np.sqrt(vec_x**2 + vec_y**2 + vec_z**2)
    
    # Zenith angle theta: angle with vertical (-Z axis)
    # cos(theta) = dot(v, -k) / |v| = -vz / r
    cos_theta = -vec_z / vec_r
    df_c['Zenith_Deg'] = np.degrees(np.arccos(cos_theta))


    # --- Plotting ---
    fig = plt.figure(figsize=(18, 12), constrained_layout=True)
    gs = fig.add_gridspec(2, 3)

    # Plot 1: Top Detector Heatmap
    ax1 = fig.add_subplot(gs[0, 0])
    h1 = ax1.hist2d(df_c['Scin0_InX'], df_c['Scin0_InY'], bins=40, range=[[-75, 75], [-75, 75]], cmap='viridis')
    ax1.set_title("Top Detector Hit Map (XY)")
    ax1.set_xlabel("X (mm)")
    ax1.set_ylabel("Y (mm)")
    plt.colorbar(h1[3], ax=ax1, label="Counts")
    ax1.set_aspect('equal')

    # Plot 2: Bottom Detector Heatmap
    ax2 = fig.add_subplot(gs[0, 1])
    h2 = ax2.hist2d(df_c['Scin3_InX'], df_c['Scin3_InY'], bins=40, range=[[-75, 75], [-75, 75]], cmap='plasma')
    ax2.set_title("Bottom Detector Hit Map (XY)")
    ax2.set_xlabel("X (mm)")
    ax2.set_ylabel("Y (mm)")
    plt.colorbar(h2[3], ax=ax2, label="Counts")
    ax2.set_aspect('equal')

    # Plot 3: Angular Distribution
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.hist(df_c['Zenith_Deg'], bins=30, color='teal', alpha=0.7, edgecolor='black')
    ax3.set_title("Reconstructed Zenith Angle")
    ax3.set_xlabel("Theta (Degrees)")
    ax3.set_ylabel("Counts")
    ax3.grid(True, alpha=0.3)

    # Plot 4: Path Length vs Energy (The Physics Check)
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.scatter(df_c['PathLen0'], df_c['Edep_Scin0'], alpha=0.3, s=10, c='purple')
    ax4.set_title("Path Length vs Energy (Scin0)")
    ax4.set_xlabel("Path Length (mm)")
    ax4.set_ylabel("Energy Deposition (MeV)")
    ax4.grid(True, linestyle='--', alpha=0.5)

    # Plot 5: dE/dx Distribution
    ax5 = fig.add_subplot(gs[1, 1])
    # dE/dx in MeV/mm
    dedx = df_c['Edep_Scin0'] / df_c['PathLen0']
    ax5.hist(dedx, bins=50, range=(0.1, 0.4), color='orange', alpha=0.7, edgecolor='black')
    ax5.set_title("dE/dx Distribution")
    ax5.set_xlabel("dE/dx (MeV/mm)")
    ax5.grid(True, alpha=0.3)

    # Plot 6: Corner Clipping Highlight
    ax6 = fig.add_subplot(gs[1, 2])
    # Define "Clipping" as short path length (< 140mm, assuming 150mm thickness)
    clipping = df_c[df_c['PathLen0'] < 140]
    normal = df_c[df_c['PathLen0'] >= 140]
    
    ax6.scatter(normal['Scin0_InX'], normal['Scin0_InY'], c='gray', alpha=0.1, s=5, label='Full Traversal')
    ax6.scatter(clipping['Scin0_InX'], clipping['Scin0_InY'], c='red', alpha=0.8, s=10, label='Clipping (<140mm)')
    ax6.set_title("Corner Clipping Locations (Top)")
    ax6.set_xlabel("X (mm)")
    ax6.set_ylabel("Y (mm)")
    ax6.legend(loc='upper right')
    ax6.set_aspect('equal')

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    print(f"Plot saved to {output_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Advanced Geant4 Physics Analysis")
    parser.add_argument("file", nargs='?', default=DEFAULT_INPUT_FILE, help="Path to ROOT file")
    parser.add_argument("--output", "-o", default=OUTPUT_FILE)
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"File not found: {args.file}")
        return

    perform_analysis(args.file, args.output)

if __name__ == "__main__":
    main()
