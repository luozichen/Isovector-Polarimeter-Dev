# Cylindrical Detector Stack Characterization (Experimental Data)

This directory contains the final, publication-grade figures and characterization results for the **cylindrical detector stack** across three different high-voltage bias levels: **800V**, **850V**, and **900V**. 

The results have been fully calibrated using cosmic ray muons, utilizing a dynamic peak-finding Landau fitting procedure to eliminate zero-density tail bias and assure absolute physical consistency.

---

## 🔬 Calibration Methodology

### 1. Dynamic Peak-Finding Landau Calibration
Standard least-squares fitting of a Landau (Moyal) distribution over a broad range (e.g. 10 to 800 mV) is heavily distorted by:
- **Low-Energy Noise & Triggers:** Dominate the spectrum below $100\text{ mV}$.
- **Zero-Density High-Energy Tail:** The massive flat tail from $600 - 800\text{ mV}$ containing zero counts disproportionately penalizes deviation in standard fit routines. This causes the fit to prematurely decay to zero, overestimating the peak location.

**Our Corrected Approach:**
1. We run a coarse-grained peak search specifically above $200\text{ mV}$ to isolate the cosmic ray muon peak.
2. The fit range start is set dynamically at `start_fit = max(10.0, Peak - 50.0) mV`.
3. The fit range end is capped strictly at `550.0 mV` to completely isolate and eliminate the zero-density tail bias.
4. **Perfect Normalization & Binning:** The fitting is performed directly on the bin centers and probability densities extracted from the same global histogram (100 bins, 10–800 mV) plotted in the final chart. This ensures perfect vertical scale and bin alignment.

### 2. Intrinsic Timing Jitter Solving
Intrinsic single-detector timing jitter ($\sigma_i$) is solved using a multi-pair coincidence approach:
- We compute pairwise time difference distributions $\Delta t_{ij} = t_i - t_j$ for all available detector pairs.
- Each pair is fitted with a standard Gaussian to extract $\sigma_{pair, ij}$.
- The system of equations $\sigma_{pair, ij}^2 = \sigma_i^2 + \sigma_j^2$ is solved via a linear least-squares matrix solver to extract the intrinsic jitter $\sigma_i$ of each detector. *(Faulty Detector 4 is excluded from all timing statistics).*

---

## 📊 Summary of Physical Results

### 1. Energy Calibration (Landau MPVs)
As PMT bias voltage increases, gain increases monotonically. The fitted Landau Most Probable Values (MPVs) scale perfectly:

| Detector | 800V MPV (mV) | 850V MPV (mV) | 900V MPV (mV) | Monotonic Rise? | Avg. Delta per 50V |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Detector 1** | **306.79** | **359.12** | **407.13** | **YES** | +50.17 mV |
| **Detector 3** | **325.07** | **347.64** | **394.42** | **YES** | +34.68 mV |
| **Detector 5** | **318.30** | **364.92** | **439.65** | **YES** | +60.68 mV |
| **Detector 6** | **351.15** | **407.67** | **470.34** | **YES** | +59.60 mV |

### 2. Intrinsic Timing Jitters
Solved single-detector intrinsic jitters ($\sigma$) also scale consistently and monotonically with high-voltage bias:

| Detector | 800V Jitter (ns) | 850V Jitter (ns) | 900V Jitter (ns) | Monotonic? |
| :---: | :---: | :---: | :---: | :---: |
| **Detector 1** | **1.184** | **1.216** | **1.426** | **YES** |
| **Detector 3** | **1.007** | **1.125** | **1.247** | **YES** |
| **Detector 5** | **1.364** | **1.528** | **1.860** | **YES** |
| **Detector 6** | **0.907** | **0.992** | **1.369** | **YES** |

---

## 🎨 Figures Index

### Energy Calibration (Landau Grids)
The final grid plots show the custom-bounded red fit curves perfectly matched in binning, scaling, and height to the data:
- **800V Stack:** `landau_fits_grid_800V.png`
- **850V Stack:** `landau_fits_grid_850V.png`
- **900V Stack:** `landau_fits_grid_900V.png`

### Timing Jitter (Gaussian Grids)
The pairwise timing difference Gaussians with a $1.5\times$ wider binning for optimal shape-tracking:
- **800V Stack:** `jitter_fits_grid_800V.png`
- **850V Stack:** `jitter_fits_grid_850V.png`
- **900V Stack:** `jitter_fits_grid_900V.png`

---

*All raw data analysis scripts and plotting routines are located in the `analysis/` root folder.*
