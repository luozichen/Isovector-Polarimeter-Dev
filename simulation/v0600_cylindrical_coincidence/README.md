# Cosmic Ray Muon Simulation (v02 Coincidence: 4-detector-stack)

This project simulates a **Cosmic Ray Muon Telescope** using Geant4. It models a vertical stack of **four** plastic scintillators to detect cosmic muons via coincidence logic.

## 1. Detector Geometry (Standard Z-Axis)

The simulation uses a **"Centered Origin"** convention, where the geometric center of the detector stack (the middle air gap) is at `(0, 0, 0)`.

*   **World Volume:** Air, $2 \times 2 \times 2$ meters.
*   **Detector Stack:** Aligned along the **Z-Axis** (Beam Axis).
*   **Coordinate System:**
    *   **Z:** Vertical Axis (Stacking Direction). +Z is Up (towards Source).
    *   **X:** PMT Axis (PMTs attached to +X face).
    *   **Y:** Width Axis.

### Module Configuration
| Component | Dimensions (mm) | Material | Position (Z Center) | ID |
| :--- | :--- | :--- | :--- | :--- |
| **Scintillator 0 (Top)** | $120(X) \times 150(Y) \times 150(Z)$ | HND-S2 (Plastic) | **+237.75 mm** | **0** |
| **Scintillator 1** | $120(X) \times 150(Y) \times 150(Z)$ | HND-S2 (Plastic) | **+79.25 mm** | **1** |
| **Scintillator 2** | $120(X) \times 150(Y) \times 150(Z)$ | HND-S2 (Plastic) | **-79.25 mm** | **2** |
| **Scintillator 3 (Bottom)** | $120(X) \times 150(Y) \times 150(Z)$ | HND-S2 (Plastic) | **-237.75 mm** | **3** |
| **Air Gaps** | 8.5 mm (x3) | Air | Between modules | - |

*   **PMT Assembly:** Attached to the **+X face** of each scintillator.
    *   Consists of Grease (0.1mm), Window (2.0mm), and Photocathode.

---

## 2. Cosmic Ray Source

The source is modeled using `G4GeneralParticleSource` (GPS) to replicate sea-level cosmic muons.

*   **Source Plane:** $30 \times 30$ cm Square Plane.
*   **Position:** Centered at **Z = +50 cm** (500 mm).
*   **Direction:** Downward (Normal vector pointing to **-Z**).
*   **Particles:** $\mu^-$ (1.0) and $\mu^+$ (1.27).
*   **Energy:** Power Law ($E^{-2.7}$) from 1 GeV to 100 GeV.
*   **Angular Distribution:** Cosine ($\cos\theta$) around the -Z axis, max angle $80^\circ$.

---

## 3. How to Run

These instructions assume you are running from a **build directory** (e.g., `build/`) inside the project root.

### A. Visualization (Interactive)
Use this to inspect the geometry and see particle tracks.

1.  **Start the Program:**
    ```bash
    ./det01
    ```
    *(A window should open showing the wireframe detector)*.

2.  **Setup "Fast" View (Recommended):**
    *In the "Idle>" prompt, type:*
    ```bash
    /control/execute ../vis_fast.mac
    ```
    *(This filters out the millions of optical photons to prevent lag)*.

3.  **Load Cosmic Source:**
    ```bash
    /control/execute ../setup_cosmic.mac
    ```

4.  **Draw Source Plane:**
    ```bash
    /vis/scene/add/gps
    ```
    *(A red square should appear above the detector)*.

5.  **Fire Events:**
    ```bash
    /run/beamOn 10
    ```

### B. Test Run (Batch Mode)
Use this to verify the simulation logic with a small dataset (100 events) without opening a window.

```bash
./det01 ../run_test.mac
```
*   **Output:** `DET01_Test_Result.root` (100 Events).

### C. Production Run (Batch Mode)
Use this for the full data collection (10,000 events).

```bash
./det01 ../run_cosmic.mac
```
*   **Output:** `DET01_Cosmic_Result.root` (10,000 Events).

---

## 4. Output Data (ROOT)

The output is an N-tuple named **"CosmicData"**.

| Branch Name | Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `EventID` | Int | - | Unique Event ID. |
| `Edep_Scin0..3` | Double | MeV | Energy deposited in Scintillator 0 (Top) to 3 (Bottom). |
| `PE_PMT0..3` | Int | Hits | Photoelectrons detected in PMT 0 (Top) to 3 (Bottom). |
| `Time_PMT0..3` | Double | ns | Arrival time of first photon in PMT 0 (Top) to 3 (Bottom). |
| `Truth_Z` | Double | mm | Z-Position of the Primary Vertex (Source Height). |

---

## 5. Macro Reference

| File | Location | Purpose |
| :--- | :--- | :--- |
| `vis.mac` | Root | **Default Visualization.** Draws everything including optical photons (Slow). |
| `vis_fast.mac` | Root | **Optimized Visualization.** Hides optical photons. Shows Muons/Electrons. |
| `setup_cosmic.mac` | Root | **Physics Configuration.** Defines the GPS source (Muons, Energy, Angles). |
| `run_test.mac` | Root | **Test Script.** Runs 100 events, saves to `DET01_Test_Result.root`. |
| `run_cosmic.mac` | Root | **Production Script.** Runs 10k events, saves to `DET01_Cosmic_Result.root`. |
