# Analysis Framework Refactor - Walkthrough

This document summarizes the completed refactoring of the Isovector Polarimeter analysis framework.

## Overview

The refactor transformed a collection of disparate scripts into a **modular Python package** with clean separation of concerns, consistent interfaces, and maintainable code.

---

## What Changed

### New Directory Structure

```
analysis/
├── config.py                 # Global configuration (enhanced)
├── process_run.py            # NEW: Main analysis script
├── compare_runs.py           # NEW: Run comparison script
├── utils/
│   ├── __init__.py
│   ├── wfm.py               # WfmReader class
│   ├── physics.py           # dCFD, Gaussian, Landau functions
│   ├── io.py                # Run finding, data loading
│   └── plotting.py          # NEW: Standardized plotting
└── legacy/                   # Archived old scripts
    ├── analyse_physical.py
    ├── compare_13_14.py
    ├── compare_15_16.py
    ├── compare_thorium_background.py
    ├── investigate_mystery.py
    └── wfm_reader.py
```

---

## New Tools

### 1. `process_run.py`

**Replaces:** `analyse_physical.py`

**Usage:**
```bash
# Analyze a single run
python3 analysis/process_run.py 17

# Analyze multiple runs
python3 analysis/process_run.py 2 3 4 5

# Analyze all available runs
python3 analysis/process_run.py --all
```

**Features:**
- Auto-detects single vs 4-channel runs
- Uses run-specific parameters from `config.get_run_params()`
- Produces identical output to legacy script (validated)

---

### 2. `compare_runs.py`

**Replaces:** `compare_13_14.py`, `compare_15_16.py`

**Usage:**
```bash
# Legacy presets (exact same output as old scripts)
python3 analysis/compare_runs.py --preset 13-14    # Run 13 vs 14 (Det 1)
python3 analysis/compare_runs.py --preset 15-16    # Run 15 vs 16 (Det 3)

# Custom comparison
python3 analysis/compare_runs.py --bg 15 --source 16 --channel 3 --bins 2
```

**Features:**
- Automatically generates 3 plots: linear (0-100mV), linear (full), log (full)
- Legacy presets for backward-compatible output
- Configurable bin width and range

---

### 3. `compare_thorium.py`

**Replaces:** `compare_thorium_background.py`

**Usage:**
```bash
# Legacy presets (4-fold stack comparisons)
python3 analysis/compare_thorium.py --preset 11-12   # 5mV threshold
python3 analysis/compare_thorium.py --preset 9-10    # 15mV threshold
python3 analysis/compare_thorium.py --preset 7-8     # 50mV threshold

# Custom comparison
python3 analysis/compare_thorium.py --bg 12 --source 11 --label "5mV"
```

**Features:**
- 2x2 grid comparison of all 4 detectors
- MeV energy calibration applied
- Normalized count density histograms

---

## Configuration

### `config.py` Enhancements

| Feature | Description |
|---------|-------------|
| `get_run_params(run_num)` | Returns run-specific Landau range, bins, and type |
| `CALIBRATION` | Detector calibration constants (MeV/mV) |
| `JITTER_SIGMA_NS` | Intrinsic jitter values per detector |
| `DETECTOR_COLORS` | Standard colors for visualization |

---

## Utils Library

### `utils/wfm.py` - WfmReader

Reads Tektronix `.wfm` binary files with proper header parsing.

```python
from analysis.utils.wfm import WfmReader

wfm = WfmReader("path/to/file.wfm")
time, volts = wfm.read_data()
# time: 1D array of time points
# volts: 2D array (num_frames, time_size)
```

### `utils/physics.py` - Analysis Functions

```python
from analysis.utils.physics import get_dcfd_time, gaussian, landau_fit_func

# Digital CFD timing extraction
t = get_dcfd_time(time_array, waveform, fraction=0.3)
```

### `utils/io.py` - Data Loading

```python
from analysis.utils.io import load_run_data, find_run_dir

# Load all data for run 17
time, data, meta = load_run_data(17)
# data: {1: volts_ch1, 2: volts_ch2, ...}
```

### `utils/plotting.py` - Visualization

```python
from analysis.utils.plotting import plot_landau_fits, plot_timing_pairs

# Produces output identical to legacy scripts
plot_landau_fits(amplitudes, cuts, run_id, config_str, landau_range, bins)
```

---

## Validation

The new `process_run.py` was validated against the legacy `analyse_physical.py`:

- ✅ **Run 017**: Output files are **byte-identical** to legacy output
- ✅ **Jitter values**: Match exactly
- ✅ **Plot appearance**: Identical (same colors, fonts, layout)

---

## Future Improvements (Deferred)

These enhancements were planned but deferred to keep the refactor focused:

1. **`run_info.json`** - Structured metadata per run (optional)
2. **Enhanced visualization** - Custom detector colors, axis labels
3. **Migration script** - Auto-generate metadata for runs 001-017

---

## Summary

| Metric | Before | After |
|--------|--------|-------|
| Main scripts | 6 | 2 |
| Code reuse | Minimal | High (utils library) |
| Configuration | Hardcoded | Centralized |
| CLI interface | None | argparse |
| Output compatibility | — | ✅ Identical |
