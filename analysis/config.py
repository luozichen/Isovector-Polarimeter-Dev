"""
Global Configuration for Isovector Polarimeter Analysis

This module centralizes all configuration parameters for the analysis pipeline.
"""
import os
from dataclasses import dataclass
from typing import Optional

# =============================================================================
# Paths
# =============================================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results", "physical")
SIMULATION_RESULTS_DIR = os.path.join(PROJECT_ROOT, "results", "simulation")

# =============================================================================
# Analysis Parameters
# =============================================================================
DEFAULT_CUT_THRESHOLD_MV = 50.0 
CFD_FRACTION = 0.3
POSITIVE_NOISE_THRESHOLD = 0.03  # 30 mV (Reject events with positive spikes)

# Landau Fitting Defaults
DEFAULT_LANDAU_BINS = 50
DEFAULT_LANDAU_LOWER = 0.01  # Volts
DEFAULT_LANDAU_UPPER = 0.4   # Volts

# =============================================================================
# Detector Calibration Constants (800V working voltage)
# From Combined Analysis (6000 events), matched with Geant4 simulation
# Reference Energy (Simulation): 30.01 MeV
# =============================================================================
CALIBRATION = {
    1: {"mpv_mV": 252.1, "mev_per_mV": 0.1190, "mV_per_MeV": 8.40},
    2: {"mpv_mV": 247.8, "mev_per_mV": 0.1211, "mV_per_MeV": 8.26},
    3: {"mpv_mV": 241.2, "mev_per_mV": 0.1244, "mV_per_MeV": 8.04},
    4: {"mpv_mV": 320.9, "mev_per_mV": 0.0935, "mV_per_MeV": 10.69},
}

# Intrinsic Jitter (from Golden Pairs analysis, 6 configurations)
JITTER_SIGMA_NS = {
    1: 0.5660,
    2: 0.5375,
    3: 0.6555,
    4: 0.4735,
}

# =============================================================================
# Plotting Configuration
# =============================================================================
DEFAULT_DPI = 150

# Standard colors for detectors
DETECTOR_COLORS = {
    1: "#1f77b4",  # Blue
    2: "#ff7f0e",  # Orange
    3: "#2ca02c",  # Green
    4: "#d62728",  # Red
}

# Comparison plot colors
COMPARISON_COLORS = {
    "background": "royalblue",
    "source": "crimson",
}

# =============================================================================
# Run-Specific Configuration
# =============================================================================
@dataclass
class RunParams:
    """Parameters for a specific run's analysis."""
    landau_lower: float = DEFAULT_LANDAU_LOWER
    landau_upper: float = DEFAULT_LANDAU_UPPER
    landau_bins: int = DEFAULT_LANDAU_BINS
    run_type: str = "4fold"  # "4fold" or "single"
    notes: Optional[str] = None


def get_run_params(run_num: int) -> RunParams:
    """
    Returns run-specific parameters based on run number.
    
    This function encapsulates the knowledge about different run configurations,
    replacing the hardcoded logic that was previously scattered in scripts.
    """
    # Default parameters
    params = RunParams()
    
    # Standard cosmic ray runs (4-fold coincidence)
    if 2 <= run_num <= 7:
        params.landau_lower = 0.01
        params.landau_upper = 0.4
        params.landau_bins = 50
        params.run_type = "4fold"
        params.notes = "Standard cosmic ray calibration run"
    
    # Thorium investigation runs
    elif run_num in [8, 9, 10]:
        params.landau_lower = 0.01
        params.landau_upper = 0.4
        params.landau_bins = 50
        params.run_type = "4fold"
        params.notes = "Thorium investigation (4-fold)"
    
    # Low threshold runs (5mV discriminator)
    elif run_num in [11, 12]:
        params.landau_lower = 0.0
        params.landau_upper = 0.3
        params.landau_bins = 60
        params.run_type = "4fold"
        params.notes = "Low threshold 5mV discriminator"
    
    # Single detector runs
    elif run_num in [13, 14]:
        params.landau_lower = 0.0
        params.landau_upper = 0.5
        params.landau_bins = 100
        params.run_type = "single"
        params.notes = "Single detector (Det 1)"
    
    elif run_num in [15, 16]:
        params.landau_lower = 0.0
        params.landau_upper = 0.5
        params.landau_bins = 100
        params.run_type = "single"
        params.notes = "Single detector (Det 3), high resolution 50mV/div"
    
    # High-voltage runs (900V)
    elif run_num >= 17:
        params.landau_lower = 0.2
        params.landau_upper = 0.6
        params.landau_bins = 100
        params.run_type = "4fold"
        params.notes = "High-stats run at 900V"
    
    return params
