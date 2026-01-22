# Jitter Analysis Methodology

This document details the methodologies used to determine the **intrinsic timing jitter ($\sigma$)** of the plastic scintillator detectors.

## 1. Introduction: What is Jitter?

In the context of scintillation detectors, "jitter" refers to the intrinsic uncertainty in the timing of the signal pulse. Even if two identical particles hit the detector at the exact same instant, the recorded signal arrival times will vary slightly due to:
1.  **Photon Statistics:** The stochastic nature of photon emission and collection.
2.  **Transit Time Spread (TTS):** Variations in the electron flight time through the PMT dynode chain.
3.  **Scintillator Geometry:** Variations in light propagation time depending on where the particle hit.

Minimizing and characterizing this jitter is critical for precise Time-of-Flight (ToF) measurements.

---

## 2. Timing Extraction: Digital CFD

For all analysis methods described below, the raw signal arrival time ($t$) is extracted using a **Digital Constant Fraction Discriminator (dCFD)**.

*   **Problem:** Using a fixed voltage threshold causes "Time Walk" — larger pulses cross the threshold earlier than smaller pulses, even if they occur at the same time.
*   **Solution:** dCFD triggers at a fixed *fraction* (30%) of the pulse peak amplitude ($V_{peak}$). This is independent of amplitude for signals with constant rise times.
*   **Algorithm:**
    1.  Find $V_{peak}$.
    2.  Set $V_{target} = 0.3 \times V_{peak}$.
    3.  Find the rising edge samples $V_i$ and $V_{i+1}$ surrounding $V_{target}$.
    4.  Linearly interpolate to find the precise time $t$.

---

## 3. Analysis Methods

We employed three distinct methods to measure the jitter, ranging from naive to highly robust.

### Method 1: Trigger-Referenced Jitter (Naive)
*   **Concept:** Assume the hardware trigger signal (formed by the 4-fold coincidence logic unit) represents the "True" cosmic ray arrival time. Measure the variation of the detector signal relative to this trigger: $\sigma_{det} \approx \sigma(t_{det} - t_{trig})$.
*   **Script:** `analyse_trigger_jitter.py`
*   **Pros:** Simple to calculate.
*   **Cons:** **Incorrect.** The trigger itself has significant jitter because it is formed by the *latest* arriving signal of the four detectors plus the logic unit's own jitter. This adds a large systematic "wobble" (0.5 - 2.0 ns) to the reference, resulting in overestimated jitter values (**0.8 - 3.0 ns**).

### Method 2: Software Collimation (Single Run)
*   **Concept:** Use data from a single run (e.g., Run 003). Solve the system of pairwise variances ($\sigma_{i}^2 + \sigma_{j}^2 = \sigma_{ij}^2$).
*   **The Problem:** In a vertical stack, the top and bottom detectors suffer from "corner-clipping" — muons hitting the edges produce weak, slow signals with poor timing.
*   **The Fix:** Apply **"Landau Cuts"**. Strictly filter events to keep only those with high amplitudes in ALL 4 detectors. This virtually "collimates" the beam to the center, removing edge effects.
*   **Script:** `analyse_jitter.py`
*   **Pros:** Can be done with a single dataset.
*   **Cons:** Requires throwing away ~50% of data. The "cuts" can introduce bias. Even with cuts, outer detectors are never as clean as middle ones.

### Method 3: Physical Collimation (Golden Approach)
*   **Concept:** The **most robust and correct method**. Instead of relying on software cuts, we use the detector geometry itself.
*   **The Physics:** When a detector is placed in the **Middle** of a 4-detector stack, the Top and Bottom detectors act as a physical collimator. A 4-fold coincidence *guarantees* that the muon passed through the central region of the middle detectors.
*   **Procedure:**
    1.  We acquired data for **6 different stack configurations** (Runs 002-007), cycling every detector through every position.
    2.  We identified the **"Golden Pairs"**: For each run, we analyze *only* the pair of detectors sitting in the middle (Pos 2 and Pos 3).
    3.  This gives us 6 high-quality pairwise measurements ($\sigma_{12}^2, \sigma_{13}^2, \sigma_{14}^2, \sigma_{23}^2, \sigma_{24}^2, \sigma_{34}^2$) where both detectors were physically collimated.
    4.  We solve the overdetermined linear system (Least Squares) to find the intrinsic $\sigma_1, \sigma_2, \sigma_3, \sigma_4$.
*   **Script:** `analyse_combined_jitter.py`
*   **Results:** Yields the true intrinsic resolution of the system (**~0.52 ns**). This method is consistent, statistically significant, and free from software selection bias.

---

## 4. The Solver (Least Squares)

For Methods 2 and 3, we solve for individual detector variances from pair measurements.
Since the jitter of two independent detectors adds in quadrature:
$$ \sigma_{ij}^2 = \sigma_i^2 + \sigma_j^2 $$

We construct a linear system $Ax = B$:
*   $x = [\sigma_1^2, \sigma_2^2, \sigma_3^2, \sigma_4^2]^T$
*   $B$ contains the measured variances of the pairs ($\sigma_{pair}^2$).
*   $A$ is the design matrix (rows of `[1, 1, 0, 0]` etc.).

We solve this using `scipy.optimize.lsq_linear` with the constraint $x > 0$.