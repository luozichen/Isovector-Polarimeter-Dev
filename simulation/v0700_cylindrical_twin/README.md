# v0500_cuboid_twin: The Custom Detector "Digital Twin"

This directory contains the high-fidelity Geant4 Monte Carlo simulation of the custom-built $150 \times 150 \times 120$ mm PVT cuboid detectors. Unlike `v0300`, which was an idealized mathematical verification, `v0500` serves as a true "Digital Twin" by injecting the physical noise, jitter, and calibration profiles measured in the laboratory (Chapter 5) into the simulation.

## The Physics Bridge & Calibration

This simulation uses the Rejection Sampling algorithm verified in `v0300` to scatter deuterons at $\theta=30^\circ$. However, it adds a critical layer of hardware realism:

### 1. Energy Calibration (Birks' Law)
The PVT detectors were calibrated in the lab using cosmic ray muons (MIPs, depositing $\approx 2$ MeV/cm). The $380$ MeV deuterons in this simulation are highly ionizing and will stop inside the $120$ mm plastic depth, suffering from **Birks' Quenching** (reduced light yield per MeV). 
* **Methodology**: We use the cosmic ray data to establish the baseline light-yield ($photons/MeV$). We then enable Birks' Law in the Geant4 physics list. Geant4 automatically calculates the saturated light output for the deuteron, allowing us to accurately predict the hardware ADC channels without guessing.

### 2. Time Jitter Deconvolution
The total timing jitter of the detector stack was measured physically in the lab ($\sigma_{total}$). However, that measurement was taken with cosmic rays traversing the $150$ mm thickness, whereas the polarimeter setup has deuterons traversing the $120$ mm thickness. We cannot directly apply the physical jitter measurement.

Instead, we use a deconvolution approach:
1. **Extract Intrinsic Noise:** $\sigma_{total}^2 = \sigma_{optical}^2 + \sigma_{electronics}^2$. We use the previous cosmic-ray simulation (`v0200`) to find $\sigma_{optical}$ for the flat orientation. We subtract this from the physical lab measurement to isolate $\sigma_{electronics}$ (the pure PMT/digitizer noise).
2. **Apply to New Orientation:** We run `v0500` to let Geant4 calculate the new optical photon transit spread ($\sigma_{optical\_new}$) for the $120$ mm traversal.
3. **Reconstruct True Jitter:** We add our derived PMT noise to the new optical spread: $\sigma_{new\_total} = \sqrt{\sigma_{optical\_new}^2 + \sigma_{electronics}^2}$.

This mathematically rigorous approach allows us to confidently predict the timing resolution of the new geometric orientation.

## Geometry Setup
- **Target**: CH2 (5x5 cm, 1 cm thick) placed at the origin.
- **Detector Array**: 16 custom cuboid detectors ($150 \times 150 \times 120$ mm) in two concentric rings at 150 cm radius.
    - **Orientation**: The $150 \times 150$ mm face points towards the target to maximize solid angle acceptance.
    - **Ring 0**: $\theta = 22.5^\circ$, 8 detectors every $45^\circ$ in $\phi$
    - **Ring 1**: $\theta = 30.0^\circ$, 8 detectors every $45^\circ$ in $\phi$

## Goal for Chapter 6 (Simulation II)
The output of `v0500` will be directly compared against `v0600` (the Cylindrical Digital Twin). By injecting the exact same polarized beam into both twins, we will definitively determine which hardware architecture provides superior polarization reconstruction precision for the final experiment.
