# Project Goal: Polarimeter Acceptance & Validation (Geant4)

## 1. Objective
Establish a "Physics Bridge" between the theoretical $M$-matrix derivations and the physical detector response. We will use Geant4 to verify that our 4-detector geometry (30° polar angle, 1.5 m distance) can accurately reconstruct beam polarisation ($P_y, T_{zz}$) despite finite detector size, solid angle effects, and target thickness.

---

## 2. Theoretical Reference
The azimuthal distribution of scattered deuterons is governed by:
$$N(\phi) \propto 1 + \frac{3}{2}P_y A_y \cos\phi + \frac{1}{2}T_{zz} A_{zz} + \frac{1}{4}(T_{xx} - T_{yy})A_{xx-yy} \cos 2\phi$$

* **Primary Target:** Measure $P_y$ (Vector) and $T_{zz}$ (Tensor).
* **Method:** Cross-ratio method for $P_y$ and Sum-Asymmetry for $T_{zz}$.
* **Coordinate System:** Madison Convention ($z$ along beam, $y$ normal to scattering plane).

---

## 3. Implementation Tasks for Coding Agent

### Phase A: The Custom Primary Generator
Standard Geant4 physics lists are spin-blind. We must "bias" the event generation in `PrimaryGeneratorAction.cc` to reflect our derivation.

- [ ] **Define Physics Parameters:** Define $P_y, T_{zz}, A_y, A_{zz}$ as variables (initially hardcoded for testing).
- [ ] **Implement Rejection Sampling:**
    1. Generate a random $\phi$ in $[0, 2\pi]$.
    2. Calculate $f(\phi) = 1 + \frac{3}{2}P_y A_y \cos\phi + \frac{1}{2}T_{zz} A_{zz}$.
    3. Generate a random $u$ in $[0, \text{Max}(f)]$.
    4. If $u < f(\phi)$, accept the event and fire the particle at $\theta=30^\circ$ and the chosen $\phi$.
- [ ] **Vertex Positioning:** Ensure particles originate randomly within the $5\text{ cm} \times 5\text{ cm} \times 1\text{ cm}$ volume of the $\text{CH}_2$ target to simulate realistic vertex distribution.

### Phase B: Detector Construction & Scoring
- [ ] **Geometry Verification:** Verify 4 detectors at $1.5\text{ m}$, $30^\circ$ from beam-line, placed at $\phi = 0^\circ, 90^\circ, 180^\circ, 270^\circ$.
- [ ] **Sensitive Detectors:** Implement a `SensitiveDetector` or `SteppingAction` to increment a counter for each deuteron that enters a detector volume.
- [ ] **Data Output:** Export total counts ($N_L, N_R, N_U, N_D$) to a CSV or console output at the end of the simulation run.

### Phase C: Validation Runs (The "Bridge")
Run simulations with the following configurations to isolate variables:

| Run # | Input $P_y$ | Input $T_{zz}$ | Expected Result |
| :--- | :--- | :--- | :--- |
| **1 (Baseline)** | 0.0 | 0.0 | $N_L \approx N_R \approx N_U \approx N_D$ (Within statistics) |
| **2 (Pure Vector)**| 0.7 | 0.0 | $N_L > N_R$; $N_U \approx N_D$ |
| **3 (Pure Tensor)**| 0.0 | 0.5 | $(N_L+N_R) \neq (N_U+N_D)$ |

---

## 4. Analysis & Reconstruction
After the simulation, take the raw "G4 counts" and attempt to reconstruct the input polarisation using our derivation:

1.  **Vector Asymmetry Calculation:**
    $$\epsilon = \frac{N_L - N_R}{N_L + N_R}$$
2.  **Reconstructed $P_y$:**
    $$P_{y, \text{recon}} = \frac{2 \epsilon}{3 A_y}$$ (Corrected for $T_{zz}$ if present).
3.  **Success Metric:** $P_{y, \text{recon}}$ must match $P_{y, \text{input}}$ within $<1\%$. 
    * *Note:* Any significant deviation represents the **Geometric Acceptance Correction Factor** required for the final thesis.

---

## 5. Next Steps
- [ ] Script `DetectorConstruction.cc` to automate the placement of the 4 units.
- [ ] Inject the rejection sampling algorithm into `PrimaryGeneratorAction.cc`.
- [ ] Run high-statistics simulations ($10^6$ events) to minimize statistical error.