import numpy as np
from scipy.stats import moyal

def gaussian(x, a, x0, sigma):
    """ Standard Gaussian function """
    return a * np.exp(-(x - x0)**2 / (2 * sigma**2))

def landau_fit_func(x, mpv, width, amp):
    """ Landau distribution wrapper using SciPy Moyal """
    return amp * moyal.pdf(x, loc=mpv, scale=width)

def get_dcfd_time(time: np.ndarray, waveform: np.ndarray, fraction: float = 0.3) -> float:
    """
    Extracts arrival time using Digital Constant Fraction Discriminator (dCFD).
    Assumes NEGATIVE polarity pulses (standard PMT).
    
    Args:
        time: Array of time points
        waveform: Array of voltage points (negative pulses)
        fraction: CFD fraction (default 0.3 or 30%)
    
    Returns:
        Interpolated time (float) or np.nan if trigger fails.
    """
    # 1. Find Peak (Minimum for negative pulse)
    idx_peak = np.argmin(waveform)
    v_peak = waveform[idx_peak]
    
    # Validation: Peak must be negative
    if v_peak > -0.0005: # Noise floor check (0.5 mV)
        return np.nan 

    # 2. Target Voltage
    v_target = fraction * v_peak
    
    # 3. Scan Rising Edge (search before peak)
    search_region = waveform[:idx_peak]
    
    # Find points that have "crossed" the target (i.e., are LOWER than target, since negative)
    # v_target is negative (e.g. -100mV). We want points < -100mV.
    candidates = np.where(search_region < v_target)[0]
    
    # If no points crossed, we can't interpolate
    if len(candidates) == 0: 
        return np.nan

    # The "crossing point" is between the last candidate and the one before it?
    # Wait, dCFD usually searches from 0 to Peak.
    # If pulse goes 0 -> -50 -> -100 (target) -> -300 (peak)
    # candidates < -100 will be the samples AFTER the crossing.
    # So the *first* candidate in the rising edge region is the one *after* crossing.
    
    # Let's re-evaluate standard logic used in old script:
    # old: candidates = np.where(search_region > v_target)[0] 
    # (Wait, old script was buggy for negative pulses? "search_region > v_target")
    # If v_peak is -300, v_target is -100.
    # 0 > -100 is True. -50 > -100 is True. -150 > -100 is False.
    # So `np.where( > )` returns indices [0, 1, ... k] where k is the sample *before* crossing.
    # Then `i = candidates[-1]` picks `k`.
    # `t_i` is time[k], `t_next` is time[k+1].
    # `v_i` > v_target, `v_next` < v_target.
    # Interpolation finds when V = v_target.
    # Yes, the old logic was correct for finding the sample *just before* crossing.
    
    candidates = np.where(search_region > v_target)[0]
    
    if len(candidates) == 0: return np.nan

    i = candidates[-1]
    
    if i >= len(search_region) - 1: return np.nan
        
    t_i = time[i]
    t_next = time[i+1]
    v_i = waveform[i]
    v_next = waveform[i+1]
    
    # 4. Interpolation
    slope = (v_next - v_i)
    if slope == 0: return t_i
        
    t_interp = t_i + (t_next - t_i) * (v_target - v_i) / slope
    return t_interp
