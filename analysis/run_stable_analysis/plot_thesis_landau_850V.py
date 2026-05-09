#!/usr/bin/env python3
"""
Thesis Defense Plot: 850V Combined Landau
Produces a beautiful 1x4 horizontal grid of combined Landau distributions.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, PROJECT_ROOT)

from analysis import config
from analysis.run_stable_analysis.analyse_stable_combined import discover_configs, load_config_data, get_middle_detectors
from analysis.utils.physics import landau_fit_func

DETECTOR_COLORS = {
    1: '#E57373', # Red
    2: '#64B5F6', # Blue
    3: '#81C784', # Green
    4: '#FFB74D', # Orange
}

RESULTS_BASE = os.path.join(PROJECT_ROOT, "results", "physical", "run_stable_results")

def main():
    voltage = "850V"
    voltage_dir = os.path.join(config.DATA_DIR, f"run_stable_{voltage}")
    if not os.path.isdir(voltage_dir):
        print(f"Error: {voltage_dir} not found")
        return
        
    output_dir = os.path.join(RESULTS_BASE, voltage)
    os.makedirs(output_dir, exist_ok=True)
    
    configs = discover_configs(voltage_dir)
    print(f"Loading data for 850V from {len(configs)} configs...")
    
    # 1. Accumulate Data (identical to analyse_stable_combined)
    det_middle_amps = {d: [] for d in range(1, 5)}
    
    for timestamp, config_str in configs:
        mid1, mid2 = get_middle_detectors(config_str)
        time_arr, data, num_events = load_config_data(voltage_dir, timestamp, config_str)
        if time_arr is None:
            continue
            
        amplitudes = {ch: np.abs(np.min(data[ch], axis=1)) for ch in data}
        
        for i in range(num_events):
            is_noise = any(np.max(data[ch][i]) > config.POSITIVE_NOISE_THRESHOLD for ch in data)
            if not is_noise:
                for det_id in [mid1, mid2]:
                    det_middle_amps[det_id].append(amplitudes[det_id][i])
                    
    # 2. Thesis Plotting Properties
    # Use larger, clean, bold fonts for presentation
    plt.rcParams.update({
        'font.size': 14,
        'font.weight': 'bold',
        'axes.titlesize': 22,
        'axes.labelsize': 20,
        'axes.labelweight': 'bold',
        'axes.titleweight': 'bold',
        'xtick.labelsize': 14,
        'ytick.labelsize': 14,
        'legend.fontsize': 12,
    })
    
    # Create 1x4 horizontal plot without the top suptitle
    fig, axes = plt.subplots(1, 4, figsize=(22, 5))
    
    landau_range = (0.05, 0.5)
    bins_count = 50
    
    for det_idx in range(4):
        det_id = det_idx + 1
        ax = axes[det_idx]
        combined_arr = np.array(det_middle_amps[det_id])
        color = DETECTOR_COLORS[det_id]
        
        if len(combined_arr) == 0:
            ax.set_title(f"Detector {det_id} (No Data)")
            continue
            
        # Draw nice histogram with thin black edge lines for presentation
        y, x, _ = ax.hist(combined_arr, bins=bins_count, range=landau_range,
                          density=False, histtype='stepfilled', alpha=0.7, 
                          color=color, edgecolor='black', linewidth=0.5)
        bin_centers = (x[:-1] + x[1:]) / 2
        
        if np.max(y) > 0:
            peak_idx = np.argmax(y)
            bin_width = bin_centers[1] - bin_centers[0]
            width_guess = bin_width * 2
            amp_guess = np.max(y) * width_guess * np.sqrt(2 * np.pi)
            
            try:
                # Rigorous fit
                popt, _ = curve_fit(landau_fit_func, bin_centers, y,
                                    p0=[bin_centers[peak_idx], width_guess, amp_guess],
                                    bounds=([0, 1e-4, 0], [2, 1, np.inf]),
                                    maxfev=10000)
                
                # Draw thick black dashed fit line
                x_fine = np.linspace(landau_range[0], landau_range[1], 200)
                ax.plot(x_fine, landau_fit_func(x_fine, *popt), 'k--', lw=2.5)
                mpv_mV = popt[0] * 1000
                
                # The exact zoom logic that perfectly bounds left and right sides
                # Find the visible histogram range (above 2% of peak height)
                nonzero_idx = np.where(y > np.max(y) * 0.02)[0]
                if len(nonzero_idx) > 0:
                    start_x = x[nonzero_idx[0]]
                    end_x = x[nonzero_idx[-1] + 1]
                    padding = (end_x - start_x) * 0.15 # 15% padding on sides
                    ax.set_xlim(max(0, start_x - padding), min(landau_range[1], end_x + padding))
                else:
                    ax.set_xlim(max(0, popt[0] - 0.08), min(landau_range[1], popt[0] + 0.18))
                
                # Beautiful opaque annotation box for thesis legibility
                textstr = f"MPV: {mpv_mV:.1f} mV\nN = {len(combined_arr)}"
                props = dict(boxstyle='round,pad=0.6', facecolor='white', alpha=0.95, edgecolor='#BDBDBD')
                ax.text(0.95, 0.95, textstr, transform=ax.transAxes, fontsize=16,
                        verticalalignment='top', horizontalalignment='right', bbox=props)
                        
            except Exception as e:
                print(f"Fit failed for Det {det_id}: {e}")
        
        ax.set_title(f"Detector {det_id} (850V)", fontweight='bold', pad=15)
        ax.set_xlabel("Amplitude (V)", labelpad=8)
        if det_idx == 0:
            ax.set_ylabel("Counts / bin", labelpad=8)
        
        # Format Y-axis to use 'k' for thousands to save space
        from matplotlib.ticker import FuncFormatter
        def k_formatter(x, pos):
            if x >= 1000:
                return f'{x/1000:.1f}k' if x % 1000 != 0 else f'{int(x/1000)}k'
            return f'{int(x)}'
        ax.yaxis.set_major_formatter(FuncFormatter(k_formatter))
        
        # Bold the borders/spines of the chart
        for spine in ax.spines.values():
            spine.set_linewidth(2.0)
            
        # Soft presentation grid
        ax.grid(True, alpha=0.25, linestyle='-', linewidth=1.5)
        
    plt.tight_layout()
    
    # Save as high-res 300 DPI for thesis print
    out_path = os.path.join(output_dir, "850V_thesis_combined_landau.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\nSaved high-res thesis plot: {out_path}")

if __name__ == "__main__":
    main()
