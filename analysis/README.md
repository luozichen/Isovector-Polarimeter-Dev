# Jitter Analysis Methodology

This document describes the method used to calculate the intrinsic timing jitter (\(\sigma\)) for four individual detectors (Det1, Det2, Det3, Det4) using cosmic ray coincidence data, as specified in `instructions.txt`.

## Objective

Calculate the intrinsic timing jitter (\(\sigma\)) for four individual detectors using cosmic ray coincidence data.

## The Problem: Geometric Noise

In a stack of 4 scintillators requiring a 4-fold coincidence, particles hitting the edges ("corner-clipping") of the top (Det1) and bottom (Det4) detectors produce weak, slow-rising signals. These signals have poor timing resolution.

If raw data is used directly, the jitter calculated for Det1 and Det4 will be artificially high and physically incorrect.

## The Solution: Software Collimation

We implement "Software Collimation" to mitigate this. We assume that "corner-clipped" events correspond to low pulse heights. By filtering the dataset to strictly enforce high-amplitude signals on **ALL** channels, we virtually "collimate" the beam to the center of the stack. This makes Det1 and Det4 as reliable as the middle detectors.

## Algorithm

### 1. Data Ingestion & Pre-processing (The Mitigation)

**Input:** A dataset where every row represents one event, containing the full waveform arrays for Ch1, Ch2, Ch3, and Ch4.

**Step A: Amplitude Calculation**
For every event, calculate the peak amplitude (\(V_{max}\)) for all 4 channels.

**Step B: The "Landau Cut"**
1.  **Analyze:** Plot the pulse height histogram for each channel to identify the "Landau Peak" (high-energy deposition region).
2.  **Define Threshold:** Set a strict voltage threshold (\(V_{cut}\)) for each channel just below this peak, excluding the low-energy noise tail.
3.  **Filter Logic:**
    *   **KEEP** event IF `(V_max_1 > V_cut_1) AND (V_max_2 > V_cut_2) AND (V_max_3 > V_cut_3) AND (V_max_4 > V_cut_4)`
    *   **DISCARD** any event that fails this check.


### 2. Timing Extraction (Digital CFD)

For the surviving "clean" events, calculate the arrival time (\(t\)) using a Digital Constant Fraction Discriminator (dCFD) to eliminate Time Walk.

*   **Parameters:** Fraction \(f = 0.3\) (30%).
*   **Method:**
    1.  Find \(V_{peak}\) of the waveform.
    2.  Calculate \(V_{target} = 0.3 \times V_{peak}\).
    3.  Scan the rising edge to find indices \(i\) and \(i+1\) such that \(V[i] < V_{target} < V[i+1]\).
    4.  **Interpolation:** Perform linear interpolation to find the precise floating-point time \(t\):

$$t = t_i + (t_{i+1} - t_i) \cdot \frac{V_{target} - V_i}{V_{i+1} - V_i}$$


### 3. Statistical Analysis (Pair Variances)

Calculate the time differences for all 6 possible pairs using the clean data:

*   $\Delta t_{12} = t_1 - t_2 \rightarrow$ Calculate Variance $\sigma_{12}^2$
*   $\Delta t_{13} = t_1 - t_3 \rightarrow$ Calculate Variance $\sigma_{13}^2$
*   ... repeat for pairs 1-4, 2-3, 2-4, 3-4.

*Note: Use a Gaussian fit to the $\Delta t$ histogram to find $\sigma$ (standard deviation), then square it to get variance.*

### 4. The Solver (Least Squares)

We have an overdetermined system of 6 equations for 4 unknowns ($x_i = \sigma_i^2$):

*   $x_1 + x_2 = \sigma_{12}^2$
*   $x_1 + x_3 = \sigma_{13}^2$
*   ... etc.

**Implementation:**
1.  Construct the Design Matrix $A$ (shape $6 \times 4$) and Observation Vector $Y$ (shape $6 \times 1$).
2.  Use `numpy.linalg.lstsq(A, Y)` to solve for $X$ ($[\sigma_1^2, \sigma_2^2, \sigma_3^2, \sigma_4^2]$).
3.  **Output:** Return $\sqrt{X}$ as the calibrated jitter for each detector.
