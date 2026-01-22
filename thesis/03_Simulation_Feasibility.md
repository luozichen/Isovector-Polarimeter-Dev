# Chapter 3: Experimental Simulation & Sensitivity Analysis

## 3.1 Overview
To confirm the feasibility of measuring the Isovector Reorientation Effect proposed by Tian et al. (2025), a simple geometric simulation is insufficient. We employ the **ImQMD (Isospin-dependent Quantum Molecular Dynamics)** model to simulate the full nuclear transport process. This allows us to account for secondary interactions, beam straggling, and background events that could obscure the subtle polarization signal.

## 3.2 Simulation Pipeline

The simulation pipeline is designed to replicate the proposed experimental setup at RIKEN.

### 3.2.1 Beam and Target
*   **Beam:** Polarized Deuteron beam (Energies consistent with Tian's paper).
*   **Polarization Initialization:** The beam is initialized with defined tensor polarization states ($t_{20} \neq 0$) by weighting the spin substates (+1, 0, -1) in the ImQMD initialization.
*   **Target:** Polyethylene (CH2) target, serving as a proton source for d-p scattering.

### 3.2.2 The Physics Engine (ImQMD)
The ImQMD model propagates the nucleons under a Hamiltonian that includes the relevant isovector potentials.
*   **Verification Goal:** We aim to observe a shift in the angular distribution of scattered deuterons when the beam polarization is toggled.
*   **Observables:** The simulation records the final momenta $(p_x, p_y, p_z)$ of all outgoing fragments.

## 3.3 Detector Response Simulation

Once the physical interaction is simulated, the outgoing particles must be "detected". This bridge is critical for verifying the detector layout.

### 3.3.1 Geometric Acceptance
We utilize the custom Python analysis suite developed for the hardware prototype (`analysis/analyse_advanced.py`) to process the ImQMD output.
*   **Path Length Corrections:** The analysis corrects for the angular dependence of energy deposition ($dE/dx$). Particles entering at oblique angles deposit more energy in the scintillator.
*   **Corner Clipping:** As observed in our Geant4 "Digital Twin" (see Chapter 5), particles clipping the edges of the detector produce partial energy signals. The simulation quantifies how many "good" physics events are lost to this effect in the proposed geometry.

### 3.3.2 Sensitivity Verification
[Placeholder: Results from the ImQMD run showing the difference in count rates $N(\theta)$ for polarized vs. unpolarized beams. This section will ideally confirm that the asymmetry $A_{yy}$ is measurable above the statistical noise floor for the proposed run time.]

## 3.4 Optimization of Detector Layout
Based on the scattering kinematics of d-p elastic scattering, the recoil proton and scattered deuteron have a specific angular correlation.
*   **Coincidence Requirement:** The simulation verifies that the 4-detector stack design covers the necessary solid angle to capture coincident d-p pairs (or d-d pairs from breakup).
*   **Result:** The current layout (vertical stack) validates the technique for cosmic ray testing, but the simulation suggests a specific angular opening is required for the actual beam experiment.
