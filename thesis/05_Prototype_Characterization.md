# Chapter 5: Prototype Characterization & Results

## 5.1 The "Digital Twin" Simulation (Geant4 v0200)

To validate the experimental data, a precise "Digital Twin" of the 4-detector stack was constructed in Geant4.

*   **Geometry:** Four scintillator blocks (120x150x150mm) spaced 8.5mm apart (air gaps).
*   **Source:** Cosmic Ray Muons generated via `G4GeneralParticleSource` with a $\cos^2\theta$ angular distribution and $E^{-2.7}$ energy spectrum.
*   **Results:**
    *   **Golden Events:** Defined as muons passing through the top face of Det 1 and bottom face of Det 4.
    *   **Energy Deposition:** The simulation predicts a Most Probable Value (MPV) of **29.85 MeV** for coincident events in the middle detectors. This value serves as the reference for energy calibration.

## 5.2 Energy Calibration

Using the 4-fold coincidence data from "Run 002" and "Run 003", we performed energy calibration.

### 5.2.1 Methodology
1.  **Landau Fitting:** The raw ADC spectra (converted from oscilloscope waveforms) were fit with Landau distributions.
2.  **Corner Clipping:** We observed "low-energy tails" in the top (Det 1) and bottom (Det 4) detectors. This is consistent with geometric acceptance—particles entering at angles clip the corners of the outer detectors but traverse the full thickness of the inner ones.
3.  **Calibration Constants:** By equating the experimental MPV (in mV) to the simulated MPV (29.85 MeV), we derived the following calibration factors:
    *   **Det 1 (Top):** 0.1095 MeV/mV
    *   **Det 2 (Mid1):** 0.1154 MeV/mV
    *   **Det 3 (Mid2):** 0.1130 MeV/mV
    *   **Det 4 (Bot):** 0.1016 MeV/mV

## 5.3 Timing Resolution (Jitter Analysis)

A key performance metric for the polarimeter is its timing resolution. We employed a "Software Collimation" technique to extract the intrinsic jitter.

### 5.3.1 Method: Software Collimation
Since we lacked a dedicated "center-only" trigger during initial runs, we used software cuts to filter out corner-clipping events.
*   **Filter:** Events were rejected if the pulse amplitude on *any* channel fell below a strict threshold (identifying it as a corner-clip).
*   **Algorithm:** Digital Constant Fraction Discriminator (dCFD) at 30% fraction.
*   **Solver:** We solved the overdetermined system of pair variances ($\sigma_i^2 + \sigma_j^2 = \sigma_{ij}^2$) to isolate individual detector contributions.

### 5.3.2 Results
The analysis of Run 003 yielded the following intrinsic timing jitters:
*   **Det 3 (Best):** $\sigma \approx 1.043$ ns
*   **Det 1 & 2:** $\sigma \approx 1.5 - 1.6$ ns
*   **Det 4:** $\sigma \approx 2.873$ ns

The poor performance of Det 4 is attributed to its position at the bottom of the stack (accumulating scattering) and potential PMT aging. However, the ~1ns resolution of the best detector confirms the viability of the design for time-of-flight measurements in the final experiment.

## 5.4 Operational Stability
*   **Noise Rejection:** The system operates with a hardware threshold of -30mV. In "Run 002", only 1.9% of triggers were rejected as noise.
*   **Burst Noise:** "Run 003" exhibited noise bursts (155 consecutive events), likely due to power supply instability on Channel 0. This requires further grounding optimization.
