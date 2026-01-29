import os
import glob
import re
import json
import numpy as np
from dataclasses import dataclass
from typing import Optional, Dict
from analysis import config
from analysis.utils.wfm import WfmReader

@dataclass
class RunMetadata:
    run_id: str
    run_num: int
    config: str
    discriminator: Optional[float] = None
    source: Optional[str] = None
    path: str = ""

def find_run_dir(run_num: int) -> Optional[str]:
    """
    Finds the directory for a specific run number in DATA_DIR.
    e.g. run_num=17 -> returns '.../data/run017_...'
    """
    pattern = os.path.join(config.DATA_DIR, f"run{run_num:03d}*")
    matches = glob.glob(pattern)
    if not matches:
        return None
    # If multiple matches, prefer the one that is a directory
    dirs = [d for d in matches if os.path.isdir(d)]
    return dirs[0] if dirs else None

def parse_run_dir_name(run_dir: str) -> RunMetadata:
    """
    Parses legacy directory naming convention.
    Format: runXYZ_EVENTS_config_ABCD_...
    """
    dirname = os.path.basename(os.path.normpath(run_dir))
    parts = dirname.split('_')
    
    # Run ID/Num
    run_str = parts[0] # run017
    run_num = int(re.search(r'\d+', run_str).group(0))
    
    # Config
    # Look for 'config' keyword
    config_str = "Unknown"
    if "config" in parts:
        idx = parts.index("config")
        if idx + 1 < len(parts):
            config_str = parts[idx+1]
    
    # Fallback: check if we have "det" and "1" etc
    if "det" in parts:
        det_idx = parts.index("det")
        config_str = f"Single_Det{parts[det_idx+1]}"

    return RunMetadata(
        run_id=run_str,
        run_num=run_num,
        config=config_str,
        path=run_dir
    )

def load_run_data(run_num: int) -> tuple[Optional[np.ndarray], Dict[int, np.ndarray], RunMetadata]:
    """
    Loads all channel data for a run.
    Returns: (time_array, {ch_id: volt_matrix}, metadata)
    """
    run_dir = find_run_dir(run_num)
    if not run_dir:
        raise ValueError(f"Run {run_num} not found in {config.DATA_DIR}")
        
    meta = parse_run_dir_name(run_dir)
    
    wfm_files = glob.glob(os.path.join(run_dir, "*_Ch*.wfm"))
    if not wfm_files:
        return None, {}, meta
        
    data = {}
    time = None
    
    # Sort files to ensure consistent order
    wfm_files.sort()
    
    min_len = float('inf')
    
    # First pass: Load all and find min length (robustness)
    temp_data = {}
    for f in wfm_files:
        # Extract channel number from filename ..._ChX.wfm
        # Usually end of string
        match = re.search(r'_Ch(\d+)\.wfm', f)
        if not match: continue
        ch = int(match.group(1))
        
        wfm = WfmReader(f)
        t, v = wfm.read_data()
        
        if time is None: 
            time = t
        
        temp_data[ch] = v
        min_len = min(min_len, v.shape[0])
        
    # Second pass: Truncate to match common length (events)
    # Note: v shape is (num_events, num_samples)
    final_data = {}
    for ch, v in temp_data.items():
        final_data[ch] = v[:min_len, :]
        
    return time, final_data, meta
