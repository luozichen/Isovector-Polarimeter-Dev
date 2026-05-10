# v0300_scattering: The "Physics Bridge" Simulation

This directory contains the Geant4 Monte Carlo simulation used to establish the "Physics Bridge" for the Isovector Polarimeter. It validates the geometric acceptance and the polarisation reconstruction algorithms.

## The Physics Bridge
Standard Geant4 hadronic physics lists (like `QGSP_BIC_XS`) are spin-blind and scatter particles isotropically. To enforce the theoretical azimuthal asymmetry of polarised deuteron scattering, we bypassed the native generator and implemented a **Rejection Sampling Algorithm** in `DET01PrimaryGeneratorAction.cc`. 

The generator randomly samples a vertex inside the target and fires a 380 MeV deuteron outwards at $\theta = 30^\circ$, with the azimuthal angle $\phi$ weighted by the cross-section derivation:
$f(\phi) = 1 + \frac{3}{2}P_y A_y \cos\phi + \frac{1}{2}T_{zz} A_{zz} + \dots$

### Geometry Setup
- **Target**: CH2 (5x5 cm, 1 cm thick) placed at the origin.
- **Detector Array**: 16 cuboid detectors ($150 \times 150 \times 120$ mm) in two concentric rings at 150 cm radius.
    - **Ring 0**: $\theta = 22.5^\circ$, 8 detectors every $45^\circ$ in $\phi$
    - **Ring 1**: $\theta = 30.0^\circ$, 8 detectors every $45^\circ$ in $\phi$ (Primary focus for $P_y / T_{zz}$ analysis).

## How to Build and Run

1. **Compile with CMake**
   ```bash
   mkdir build && cd build
   cmake ..
   make -j4
   ```
2. **Batch Mode (1000 events)**
   ```bash
   ./det01 run_beam.mac
   ```
   *Note: This generates `DET01_Scattering_Result.root`.*

## Analysis & The "Crosstalk" Discovery

Initial analysis runs checking for any photoelectrons (`PE > 0`) yielded heavily diluted asymmetries:
```text
N_L (0 deg)  : 203
N_U (90 deg) : 179
N_R (180 deg): 165
N_D (270 deg): 192
Left-Right Asymmetry (e_LR): 0.103
```

**Discovery:** Geant4 simulates secondary radiation perfectly. A single primary deuteron depositing 20+ MeV creates ~250,000 optical photons in the target detector. However, secondary gamma rays or escaping neutrons can strike adjacent detectors, creating 1-5 photons. The naive `PE > 0` condition counted this "crosstalk" as real hits, artificially inflating the counts of every detector and washing out the physical asymmetry.

**Solution:** In a real hardware setup, a Constant Fraction Discriminator (CFD) threshold is used to filter noise. Applying a software threshold of `Edep > 10.0 MeV` in our ROOT analysis script (`check_v0300.C`) effectively ignores the crosstalk, allowing the true polarised physics asymmetry to be reconstructed.
