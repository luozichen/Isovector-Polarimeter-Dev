# v0300_scattering: Deuteron Scattering Simulation

This directory contains the Geant4 simulation for the deuteron beam scattering off a CH2 target.

## Setup
- **Target**: CH2 (5x5 cm, 1 cm thick) placed at the origin.
- **Beam**: 190 MeV/u Deuteron beam (380 MeV total) along the +Z axis, originating slightly upstream from the target.
- **Detector Array**: 4 detectors (120x150x150 mm) arranged with their 15x15 cm faces pointing at the target (PMT opening facing away), 50 cm from the target, at a polar scattering angle of 15°, evenly distributed every 90° in azimuth.

## How to Build and Run

1. **Create build directory**
   ```bash
   mkdir build && cd build
   ```
2. **Compile with CMake**
   ```bash
   cmake ..
   make
   ```
3. **Visualization Mode (Execute step by step to visualize)**
   ```bash
   ./det01
   /control/execute vis.mac
   /control/execute setup_beam.mac
   /run/beamOn 10
   ```
4. **Batch Mode (1000 events)**
   ```bash
   ./det01 run_beam.mac
   ```

*Note: The generated output ROOT file will be saved as `coincidence.root` in the build directory.*
