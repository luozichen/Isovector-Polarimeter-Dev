"""
Jitter Calculation Utilities for Isovector Polarimeter Analysis

This module provides the core infrastructure for jitter analysis:
- Collimation algorithms (software filtering strategies)
- Jitter system solver (least-squares for pairwise variances)
- Timing extraction utilities
"""

import numpy as np
from scipy.optimize import lsq_linear
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from analysis import config
from analysis.utils.physics import get_dcfd_time


# =============================================================================
# COLLIMATION ALGORITHMS
# =============================================================================

class CollimationAlgorithm(ABC):
    """
    Abstract base class for software collimation algorithms.
    
    Collimation algorithms filter events to improve timing resolution by
    selecting muons that passed through favorable regions of the detector.
    """
    
    name: str = "base"
    
    @abstractmethod
    def calculate_cuts(
        self, 
        amplitudes: Dict[int, np.ndarray], 
        config_str: str
    ) -> Dict[int, float]:
        """
        Calculate amplitude cuts for each channel.
        
        Args:
            amplitudes: Dict mapping channel number to amplitude arrays (Volts)
            config_str: Stack configuration string (e.g., "1234")
            
        Returns:
            Dict mapping channel number to cut values (Volts)
        """
        pass
    
    def categorize_events(
        self,
        data: Dict[int, np.ndarray],
        amplitudes: Dict[int, np.ndarray],
        cuts: Dict[int, float],
        num_events: int,
        config_str: str = ""
    ) -> Tuple[List[int], List[int], List[int]]:
        """
        Categorize events into clean, clipped, and noise.
        
        Returns:
            Tuple of (clean_indices, clipped_indices, noise_indices)
        """
        clean_indices = []
        clipped_indices = []
        noise_indices = []
        
        for i in range(num_events):
            # 1. Check Electronic Noise (Positive Excursion)
            is_electronic_noise = False
            for ch in data:
                if np.max(data[ch][i]) > config.POSITIVE_NOISE_THRESHOLD:
                    is_electronic_noise = True
                    break
            
            if is_electronic_noise:
                noise_indices.append(i)
                continue
                
            # 2. Check Clipping (Low Amplitude)
            is_clipped = False
            for ch in data:
                if amplitudes[ch][i] < cuts[ch]:
                    is_clipped = True
                    break
                    
            if is_clipped:
                clipped_indices.append(i)
            else:
                clean_indices.append(i)
                
        return clean_indices, clipped_indices, noise_indices


class LandauCutAlgorithm(CollimationAlgorithm):
    """
    Landau Peak Cut Algorithm (Default)
    
    - Top/Bottom detectors: 90% of Landau peak (removes corner-clipped events)
    - Middle detectors: Only 50 mV floor (energy deposition skewed upward)
    """
    
    name = "type_a"
    
    def calculate_cuts(
        self, 
        amplitudes: Dict[int, np.ndarray], 
        config_str: str
    ) -> Dict[int, float]:
        cuts = {}
        
        for ch, amps in amplitudes.items():
            # Find detector position in stack
            det_char = str(ch)
            if det_char in config_str:
                position = config_str.index(det_char)
            else:
                position = -1
            
            # Calculate Landau peak
            counts, bins = np.histogram(amps, bins=100, range=(0, 0.5))
            bin_centers = (bins[:-1] + bins[1:]) / 2
            peak_idx = np.argmax(counts)
            peak_val = bin_centers[peak_idx]
            
            # Position-dependent cut
            if position == 0 or position == 3:
                # Top or Bottom: Apply 90% of Landau peak
                cut_val = max(config.DEFAULT_CUT_THRESHOLD_MV / 1000.0, peak_val * 0.9)
            else:
                # Middle detectors: Only floor cut
                cut_val = config.DEFAULT_CUT_THRESHOLD_MV / 1000.0
            
            cuts[ch] = cut_val
        
        return cuts


class NoCutAlgorithm(CollimationAlgorithm):
    """
    No Cut Algorithm
    
    Only applies the minimum 50 mV floor to all detectors.
    No Landau-based cuts are applied.
    """
    
    name = "none"
    
    def calculate_cuts(
        self, 
        amplitudes: Dict[int, np.ndarray], 
        config_str: str
    ) -> Dict[int, float]:
        return {ch: config.DEFAULT_CUT_THRESHOLD_MV / 1000.0 for ch in amplitudes}


class EventWiseLandauAlgorithm(CollimationAlgorithm):
    """
    Type B: Event-Wise Landau Cut Algorithm
    
    For each single event:
    1. Calculate dynamic threshold = 0.9 * min(mid1, mid2)
    2. Discard event if Top < Threshold OR Bottom < Threshold
    
    This essentially enforces that the top and bottom detectors must see energy 
    commensurate with what the middle detectors saw, effectively removing corner-clipped events.
    """
    
    name = "type_b"
    
    def calculate_cuts(
        self, 
        amplitudes: Dict[int, np.ndarray], 
        config_str: str
    ) -> Dict[int, float]:
        # This algorithm doesn't use static cuts, but we return the floor 
        # for visualization compatibility
        return {ch: config.DEFAULT_CUT_THRESHOLD_MV / 1000.0 for ch in amplitudes}
        
    def categorize_events(
        self,
        data: Dict[int, np.ndarray],
        amplitudes: Dict[int, np.ndarray],
        cuts: Dict[int, float],
        num_events: int,
        config_str: str = ""
    ) -> Tuple[List[int], List[int], List[int]]:
        
        clean_indices = []
        clipped_indices = []
        noise_indices = []
        
        # Identify detector roles
        if not config_str:
            # Fallback if no config string provided
            return super().categorize_events(data, amplitudes, cuts, num_events, config_str)
            
        mid1_id, mid2_id = get_middle_detectors(config_str)
        top_id = int(config_str[0])
        bot_id = int(config_str[3])
        
        # Floor threshold (to avoid noise)
        FLOOR_MOISE_THRESHOLD = config.DEFAULT_CUT_THRESHOLD_MV / 1000.0  # 50 mV
        
        for i in range(num_events):
            # 1. Check Electronic Noise
            is_noise = False
            for ch in data:
                if np.max(data[ch][i]) > config.POSITIVE_NOISE_THRESHOLD:
                    is_noise = True
                    break
            if is_noise:
                noise_indices.append(i)
                continue
            
            # 2. Check Clipping (Type B Logic)
            
            # Get amplitudes for this event
            amp_mid1 = amplitudes[mid1_id][i]
            amp_mid2 = amplitudes[mid2_id][i]
            amp_top = amplitudes[top_id][i]
            amp_bot = amplitudes[bot_id][i]
            
            # Calculate dynamic threshold
            min_mid = min(amp_mid1, amp_mid2)
            dynamic_threshold = 0.9 * min_mid
            
            # Apply cut:
            # Top AND Bottom must be >= dynamic_threshold
            # AND all channels must be >= 50mV floor
            
            is_clipped = False
            
            # Check floor first
            if (amp_mid1 < FLOOR_MOISE_THRESHOLD or 
                amp_mid2 < FLOOR_MOISE_THRESHOLD or 
                amp_top < FLOOR_MOISE_THRESHOLD or 
                amp_bot < FLOOR_MOISE_THRESHOLD):
                is_clipped = True
            
            # Check dynamic threshold
            elif amp_top < dynamic_threshold or amp_bot < dynamic_threshold:
                is_clipped = True
                
            if is_clipped:
                clipped_indices.append(i)
            else:
                clean_indices.append(i)
                
        return clean_indices, clipped_indices, noise_indices 

# Registry of available algorithms
COLLIMATION_ALGORITHMS = {
    "type_a": LandauCutAlgorithm,
    "none": NoCutAlgorithm,
    "type_b": EventWiseLandauAlgorithm,
}


def get_collimation_algorithm(name: str) -> CollimationAlgorithm:
    """Get a collimation algorithm by name."""
    if name not in COLLIMATION_ALGORITHMS:
        raise ValueError(f"Unknown algorithm: {name}. Available: {list(COLLIMATION_ALGORITHMS.keys())}")
    return COLLIMATION_ALGORITHMS[name]()


# =============================================================================
# JITTER SOLVER
# =============================================================================

@dataclass
class JitterResult:
    """Result of jitter analysis for a detector set."""
    sigmas: np.ndarray  # Individual detector jitters (ns)
    pair_variances: np.ndarray  # Measured pair variances (ns^2)
    design_matrix: np.ndarray  # A matrix used in solver
    residual: float  # Least squares residual


def solve_jitter_system(pair_variances: List[float]) -> JitterResult:
    """
    Solve for individual detector jitters from pairwise variances.
    
    Uses least-squares with non-negativity constraint.
    
    System: σ²(pair_ij) = σ²(i) + σ²(j)
    
    Args:
        pair_variances: List of 6 pair variances in order:
                       (1-2, 1-3, 1-4, 2-3, 2-4, 3-4)
    
    Returns:
        JitterResult with individual sigmas and diagnostics
    """
    A = np.array([
        [1, 1, 0, 0],  # 1-2
        [1, 0, 1, 0],  # 1-3
        [1, 0, 0, 1],  # 1-4
        [0, 1, 1, 0],  # 2-3
        [0, 1, 0, 1],  # 2-4
        [0, 0, 1, 1],  # 3-4
    ])
    
    y = np.array(pair_variances)
    
    # Filter NaN values
    valid_mask = ~np.isnan(y)
    if np.sum(valid_mask) < 4:
        return JitterResult(
            sigmas=np.full(4, np.nan),
            pair_variances=y,
            design_matrix=A,
            residual=np.nan
        )
    
    res = lsq_linear(A[valid_mask], y[valid_mask], bounds=(0, np.inf))
    sigmas = np.sqrt(res.x)
    
    return JitterResult(
        sigmas=sigmas,
        pair_variances=y,
        design_matrix=A,
        residual=res.cost
    )


# =============================================================================
# TIMING EXTRACTION
# =============================================================================

def extract_timing_for_events(
    time: np.ndarray,
    data: Dict[int, np.ndarray],
    indices: List[int],
    cfd_fraction: float = None
) -> Dict[int, np.ndarray]:
    """
    Extract dCFD timings for specified events.
    
    Args:
        time: Time array (seconds)
        data: Dict mapping channel to waveform matrices
        indices: Event indices to process
        cfd_fraction: CFD fraction (default from config)
        
    Returns:
        Dict mapping channel to timing arrays (seconds)
    """
    if cfd_fraction is None:
        cfd_fraction = config.CFD_FRACTION
        
    times = {ch: [] for ch in data}
    
    for idx in indices:
        for ch in data:
            t = get_dcfd_time(time, data[ch][idx], cfd_fraction)
            times[ch].append(t)
            
    return {ch: np.array(times[ch]) for ch in times}


def calculate_pair_timing(
    times: Dict[int, np.ndarray],
    pair: Tuple[int, int]
) -> Tuple[np.ndarray, float, float]:
    """
    Calculate time differences for a detector pair.
    
    Args:
        times: Dict mapping channel to timing arrays (seconds)
        pair: Tuple of (det_A, det_B)
        
    Returns:
        Tuple of (delta_t array in ns, mean, sigma)
    """
    chA, chB = pair
    tA = times[chA]
    tB = times[chB]
    
    mask = (~np.isnan(tA)) & (~np.isnan(tB))
    delta_t = (tA[mask] - tB[mask]) * 1e9  # Convert to ns
    
    if len(delta_t) == 0:
        return np.array([]), np.nan, np.nan
    
    mean = np.mean(delta_t)
    sigma = np.std(delta_t)
    
    return delta_t, mean, sigma


def get_all_pair_variances(times: Dict[int, np.ndarray]) -> List[float]:
    """
    Calculate variances for all 6 detector pairs.
    
    Returns:
        List of 6 pair variances (ns^2) in order:
        (1-2, 1-3, 1-4, 2-3, 2-4, 3-4)
    """
    pairs = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
    variances = []
    
    for pair in pairs:
        _, _, sigma = calculate_pair_timing(times, pair)
        variances.append(sigma ** 2)
    
    return variances


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_middle_detectors(config_str: str) -> Tuple[int, int]:
    """
    Get the detector IDs in the middle positions (1 and 2).
    
    Args:
        config_str: Stack configuration string (e.g., "1234")
        
    Returns:
        Tuple of (mid1_det, mid2_det)
    """
    if len(config_str) != 4:
        return (2, 3)  # Default
    return (int(config_str[1]), int(config_str[2]))


def get_detector_position(det_id: int, config_str: str) -> int:
    """
    Get the physical position (0=Top, 1=Mid1, 2=Mid2, 3=Bot) for a detector.
    
    Returns -1 if not found.
    """
    det_char = str(det_id)
    if det_char in config_str:
        return config_str.index(det_char)
    return -1
