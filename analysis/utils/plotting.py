"""
Standardized Plotting Utilities for Isovector Polarimeter Analysis

This module provides consistent, reusable plotting functions for all analysis scripts.
These functions are designed to produce output IDENTICAL to the original analyse_physical.py
to ensure backward compatibility during the refactoring process.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from typing import Dict, List, Optional, Tuple
import os

from analysis import config
from analysis.utils.physics import gaussian, landau_fit_func


def get_position_label(det_id: int, config_str: str) -> str:
    """
    Returns the physical position label (Top, Mid1, Mid2, Bot) 
    for a given Detector ID (1-4) based on the config string.
    
    Args:
        det_id: Detector ID (1-4)
        config_str: Stack configuration string, e.g., "1234"
        
    Returns:
        Position label string
    """
    det_char = str(det_id)
    if det_char not in config_str:
        return "Unknown"
    
    idx = config_str.index(det_char)
    positions = ["Top", "Mid1", "Mid2", "Bot"]
    if idx < len(positions):
        return positions[idx]
    return "Unknown"


def plot_landau_fits(
    amplitudes: Dict[int, np.ndarray],
    cuts: Dict[int, float],
    run_id: str,
    config_str: str,
    landau_range: Tuple[float, float],
    bins_count: int,
    output_dir: Optional[str] = None
) -> str:
    """
    Plots Pulse Height Distributions with Landau Fits for all channels.
    Matches the exact output of the original analyse_physical.py.
    
    Args:
        amplitudes: Dict mapping channel number to amplitude arrays (in Volts)
        cuts: Dict mapping channel number to cut values (in Volts)
        run_id: Run identifier string
        config_str: Stack configuration string
        landau_range: Tuple of (lower, upper) bounds for histogram
        bins_count: Number of bins for histogram
        output_dir: Output directory (defaults to config.RESULTS_DIR)
        
    Returns:
        Path to saved figure
    """
    if output_dir is None:
        output_dir = config.RESULTS_DIR
    os.makedirs(output_dir, exist_ok=True)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    fig.suptitle(f"{run_id} (Config {config_str}) - Energy Deposition")
    
    for i, ch in enumerate(range(1, 5)):
        ax = axes[i]
        vals = np.array(amplitudes[ch])
        
        # Histogram - matches original exactly
        y, x, _ = ax.hist(vals, bins=bins_count, range=landau_range, 
                          density=False, histtype='stepfilled', alpha=0.4, label='Data')
        
        bin_centers = (x[:-1] + x[1:]) / 2
        
        # Fit
        if len(vals) > 0 and np.max(y) > 0:
            peak_idx = np.argmax(y)
            mpv_guess = bin_centers[peak_idx]
            try:
                mpv_limit = max(1.0, landau_range[1] * 1.2)
                popt, _ = curve_fit(
                    landau_fit_func, bin_centers, y, 
                    p0=[mpv_guess, 0.01, np.max(y) * 0.01], 
                    bounds=([0, 0, 0], [mpv_limit, 1, np.inf])
                )
                
                x_fine = np.linspace(landau_range[0], landau_range[1], 200)
                ax.plot(x_fine, landau_fit_func(x_fine, *popt), 'r-', lw=2, 
                        label=f'Fit\nMPV={popt[0]*1000:.1f} mV')
            except Exception as e:
                print(f"  [Warning] Ch{ch} fit failed: {e}")
            
        cut_val = cuts[ch]
        ax.axvline(cut_val, color='k', linestyle='--', label=f'Cut: {cut_val*1000:.1f} mV')
        
        det_id = ch
        pos_label = get_position_label(det_id, config_str)
        ax.set_title(f"Ch{ch} - Det {det_id} [{pos_label}]")
        ax.set_xlabel("Amplitude (V)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_path = os.path.join(output_dir, f"{run_id}_landau_fits.png")
    plt.savefig(out_path)
    plt.close(fig)
    print(f"  Saved landau fits: {out_path}")
    
    return out_path


def plot_timing_pairs(
    times: Dict[int, np.ndarray],
    run_id: str,
    config_str: str = "1234",
    output_dir: Optional[str] = None
) -> Tuple[str, List[float]]:
    """
    Plots time difference distributions for all detector pairs.
    Matches the exact output of the original analyse_physical.py.
    
    Args:
        times: Dict mapping channel number to timing arrays (in seconds)
        run_id: Run identifier string
        config_str: Stack configuration string (unused in original, kept for API)
        output_dir: Output directory (defaults to config.RESULTS_DIR)
        
    Returns:
        Tuple of (path to saved figure, list of pair variances)
    """
    if output_dir is None:
        output_dir = config.RESULTS_DIR
    os.makedirs(output_dir, exist_ok=True)
    
    pairs = [(1,2), (1,3), (1,4), (2,3), (2,4), (3,4)]
    
    fig_pairs, axes_pairs = plt.subplots(2, 3, figsize=(15, 10))
    axes_pairs = axes_pairs.flatten()
    fig_pairs.suptitle(f"{run_id} - Time Differences (Clean Events)")
    
    pair_vars = []
    
    for i, (chA, chB) in enumerate(pairs):
        ax = axes_pairs[i]
        tA = times[chA]
        tB = times[chB]
        mask = (~np.isnan(tA)) & (~np.isnan(tB))
        delta_t = (tA[mask] - tB[mask]) * 1e9  # ns
        
        mean = np.mean(delta_t)
        std = np.std(delta_t)
        
        # Gaussian Fit - matches original exactly
        counts, bins, _ = ax.hist(delta_t, bins=30, alpha=0.6, density=True)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        sigma = std
        try:
            popt, _ = curve_fit(gaussian, bin_centers, counts, p0=[1.0, mean, std])
            sigma = abs(popt[2])
            x_fine = np.linspace(bins[0], bins[-1], 100)
            ax.plot(x_fine, gaussian(x_fine, *popt), 'r-', lw=2)
        except:
            pass
            
        pair_vars.append(sigma**2)
        # Match original title format exactly
        ax.set_title(f"Ch{chA}-Ch{chB} (Det {chA}-{chB})\nSigma = {sigma:.3f} ns")
        ax.set_xlabel("Delta T (ns)")

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_path = os.path.join(output_dir, f"{run_id}_timing_pairs.png")
    plt.savefig(out_path)
    plt.close()
    print(f"  Saved timing pairs: {out_path}")
    
    return out_path, pair_vars


def plot_waveforms(
    time: np.ndarray,
    data: Dict[int, np.ndarray],
    indices: List[int],
    run_id: str,
    label: str,
    suffix: str,
    max_plots: int = 5,
    output_dir: Optional[str] = None
) -> Optional[str]:
    """
    Plots sample waveforms for visual inspection.
    Matches the exact output of the original analyse_physical.py.
    
    Args:
        time: Time array (in seconds)
        data: Dict mapping channel number to waveform matrices
        indices: Event indices to plot
        run_id: Run identifier string
        label: Plot title label
        suffix: Filename suffix
        max_plots: Maximum number of waveforms to plot
        output_dir: Output directory
        
    Returns:
        Path to saved figure or None if no indices
    """
    if not indices:
        return None
        
    if output_dir is None:
        output_dir = config.RESULTS_DIR
    os.makedirs(output_dir, exist_ok=True)

    indices_to_plot = indices[:max_plots]
    n = len(indices_to_plot)
    
    fig, axes = plt.subplots(n, 1, figsize=(10, 3*n), sharex=True)
    if n == 1:
        axes = [axes]
    
    fig.suptitle(f"{run_id} - {label}", fontsize=16)
    
    for i, idx in enumerate(indices_to_plot):
        ax = axes[i]
        # Match original: iterate range(1, 5) with default colors
        for ch in range(1, 5):
            ax.plot(time*1e9, data[ch][idx]*1000, label=f"Ch{ch}")
        
        ax.set_title(f"Event #{idx}")
        ax.set_ylabel("mV")
        ax.grid(True, alpha=0.3)
        if i == 0:
            ax.legend(loc='upper right')
        
    axes[-1].set_xlabel("Time (ns)")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_path = os.path.join(output_dir, f"{run_id}_{suffix}.png")
    plt.savefig(out_path)
    plt.close(fig)
    print(f"  Saved {suffix}: {out_path}")
    
    return out_path


def plot_comparison(
    amps_bg: np.ndarray,
    amps_source: np.ndarray,
    bins: np.ndarray,
    title: str,
    filename: str,
    label_bg: str = "Background",
    label_source: str = "Source",
    log_y: bool = False,
    output_dir: Optional[str] = None
) -> str:
    """
    Plots comparison histogram of two datasets (e.g., background vs source).
    
    Args:
        amps_bg: Background amplitudes (in mV)
        amps_source: Source amplitudes (in mV)
        bins: Histogram bins
        title: Plot title
        filename: Output filename
        label_bg: Label for background dataset
        label_source: Label for source dataset
        log_y: Whether to use log scale for y-axis
        output_dir: Output directory
        
    Returns:
        Path to saved figure
    """
    if output_dir is None:
        output_dir = config.RESULTS_DIR
    os.makedirs(output_dir, exist_ok=True)
    
    plt.figure(figsize=(12, 7))
    
    plt.hist(amps_bg, bins=bins, histtype='step', linewidth=2, 
             color=config.COMPARISON_COLORS["background"], 
             label=f'{label_bg}')
    
    plt.hist(amps_source, bins=bins, histtype='step', linewidth=2, 
             color=config.COMPARISON_COLORS["source"], 
             label=f'{label_source}')
    
    plt.title(title, fontsize=14)
    plt.xlabel("Peak Amplitude (mV)")
    plt.ylabel("Counts")
    
    if log_y:
        plt.yscale('log')
        plt.ylabel("Counts (Log Scale)")
        
    plt.legend()
    plt.grid(True, alpha=0.3, which="both")
    
    out_path = os.path.join(output_dir, filename)
    plt.savefig(out_path, dpi=config.DEFAULT_DPI)
    plt.close()
    print(f"Saved: {out_path}")
    
    return out_path
