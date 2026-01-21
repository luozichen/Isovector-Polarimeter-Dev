# Deuteron Isovector Polarimeter Development

| **Project Info** | Details |
| :--- | :--- |
| **Author** | **Zichen Luo** |
| **Institution** | Tsinghua University, Department of Physics |
| **Supervisor** | Prof. Xiao Zhigang |
| **Focus** | Hardware Dev & Geant4 Simulation |

## 📍 Project Goal

### Detector Hardware Development
- [x] Electronics Design: Iteratively design and solder the PMT Voltage Divider PCB.
- [x] Mechanical Structure: Design and 3D print the base and light-tight casing.
- [x] System Integration: Complete the optical coupling of scintillators to PMTs and the final assembly of 4 detector units.
- [x] Cosmic Ray Testing: Construct a cosmic ray telescope system to verify the detector's logic coincidence and long-term operational stability.
- [ ] ~~Energy Calibration: Utilize the laboratory's Thorium source (Th-232) to perform precise energy calibration.~~
- [x] Digital Twin Simulation: Create a Geant4 "digital twin" of the detector stack and run simulations to obtain expected energy deposition distributions.
- [x] Energy Calibration: Perform energy calibration by matching experimental Cosmic Ray Muon Landau distributions with Geant4 simulated energy deposits (replacing Th-232 method).
- [ ] Time Resolution: Measure detector jitter and time resolution.

### Theoretical Derivation & Physics Simulation
- [ ] Polarization Derivation: Starting from quantum scattering theory, derive the analytical relationship between the deuteron-proton (d-p) elastic scattering cross-section and the beam's tensor polarization.
- [ ] Detection Simulation: Write code to simulate the scattering of the polarized deuteron beam on a methlyne target, and obtain the detector response, verifying the derivation and the rationality of the detector layout.
- [ ] Physics Verification: Using the ImQMD transport model to simulate the entire IVR experiment process, verifying the sensitivity of the experimental results to the beam polarization.
---

## 📅 Development Log

### January 2026
* **2026-01-21:**
   * Started a 1M long **Geant4 (G4) simulation** run to get better data (not physical detector data).
   * **Theoretical Derivation Started:**
     * Began deep dive into deuteron polarization scattering theory.
     * Currently analyzing:
       * M matrix properties and constraints by symmetry.
       * Analyzing power definitions.
       * Beam polarization formalism.
       * Spherical tensor operators.
       * Madison convention standards.
   * **Jitter Analysis (Software Collimation):**
     * **Objective:** Determine intrinsic timing jitter ($\sigma$) for individual detectors using cosmic ray data.
     * **Methodology:**
       * **Software Collimation:** Implemented "Landau Cuts" to filter out low-amplitude "corner-clipping" events which degrade timing resolution. (Kept 631/1000 events from Run 003).
       * **Timing Extraction:** Used Digital Constant Fraction Discriminator (dCFD) at 30% fraction with linear interpolation.
       * **Solver:** Solved the overdetermined system of pair variances ($\sigma_i^2 + \sigma_j^2 = \sigma_{ij}^2$) to extract individual detector jitter.
     * **Tool:** Created `analysis/analyse_physical.py` (replaces CSV-based tools).
     * **Results (Run 003):**
       * **Det 1:** 1.313 ns
       * **Det 2:** 0.000 ns (Solver artifact, indicates excellent performance or limits of statistics)
       * **Det 3:** 0.000 ns
       * **Det 4:** 1.423 ns
   * **Infrastructure Update:**
     * **Directory Reorganization:** Separated results into `results/physical/` (experimental data) and `results/simulation/` (Geant4 outputs) for better organization.
     * **Analysis Pipeline Upgrade:** Transitioned from parsing `.csv` files to reading binary `.wfm` files directly. This handles **FastFrame** acquisitions natively and significantly speeds up processing.
   * **New Data Acquisition (Stack 2134):**
     * **Configuration:** Det 2 (Top) -> Det 1 (Mid1) -> Det 3 (Mid2) -> Det 4 (Bot).
     * **Goal:** Place Det 1 and Det 3 in the geometric center of the stack to acquire "golden" vertical events naturally, validating the software collimation results.
     * **Status:** Acquisition started.
   * **Experimental Status:**
     * **Run 001:** 10 test events. 1 clipped, 1 noise.
     * **Run 002 (1234):** 1000 events. 78% clean. Jitter: ~1.1ns (Det1), ~0.5ns (Det2), ~1.2ns (Det4).
     * **Run 003 (2143):** 1000 events. 59% clean. High noise (271 events). Jitter: ~1.3ns (Det1), ~1.4ns (Det4).
     * **Run 004 (2134):** Acquisition started.

* **2026-01-20:**
   * Started a 1M long **Geant4 (G4) simulation** run to get better data (not physical detector data).
   * **Theoretical Derivation Started:**
     * Began deep dive into deuteron polarization scattering theory.
     * Currently analyzing:
       * M matrix properties and constraints by symmetry.
       * Analyzing power definitions.
       * Beam polarization formalism.
       * Spherical tensor operators.
       * Madison convention standards.
   * **Jitter Analysis (Software Collimation):**
     * **Objective:** Determine intrinsic timing jitter ($\sigma$) for individual detectors using cosmic ray data.
     * **Methodology:**
       * **Software Collimation:** Implemented "Landau Cuts" to filter out low-amplitude "corner-clipping" events which degrade timing resolution. (Kept 631/1000 events from Run 003).
       * **Timing Extraction:** Used Digital Constant Fraction Discriminator (dCFD) at 30% fraction with linear interpolation.
       * **Solver:** Solved the overdetermined system of pair variances ($\sigma_i^2 + \sigma_j^2 = \sigma_{ij}^2$) to extract individual detector jitter.
     * **Tool:** Created `analysis/analyse_jitter.py`.
     * **Results (Run 003):**
       * **Det 1:** 1.643 ns
       * **Det 2:** 1.490 ns
       * **Det 3:** 1.043 ns (Best Performance)
       * **Det 4:** 2.873 ns (Needs investigation)
     * **Future Plan:** Perform higher-quality measurements by physically placing different detector pairs in the center of the stack (position 2 and 3). This will ensure "golden" vertical events for all detectors without requiring software collimation/filtering. Scheduled for the next available lab session.
* **2026-01-19:**
   * ❄️❄️ *Official start of the Winter Holidays.*
   * **Run 003 Analysis (Switched Detectors):**
     * **Status:** Analyzed 1000 events from the "switched" configuration (Inner/Outer detectors swapped).
     * **Noise/Stability:** Observed significantly higher noise floor compared to Run 002. Mean baseline noise rose to ~50-60mV.
       * Rejection Rate: **27.1% (271/1000)** rejected with the standard 30mV threshold (vs 1.9% in Run 002).
     * **Burst Noise Investigation:**
       * Identified a major noise burst lasting **155 consecutive events** (Indices 136-290).
       * Identified a secondary burst of 58 events (Indices 505-562).
       * This explains the rapid count increase observed during acquisition.
     * **Results:** Successfully generated Landau fits for the 729 clean events. Plots updated with Run ID labels for clarity.
   * **Energy Calibration Update:**
     * **Methodology Change:** Re-evaluated the "True Energy" reference from Geant4 simulation.
       * *Golden Events (Face-to-Face):* Selecting strictly vertical muons passing through the top face of the top detector and bottom face of the bottom detector. Result: **29.50 MeV**.
       * *Realistic (4-Fold Coincidence):* Selecting all events that trigger the 4-fold coincidence (matching experiment). Averaged the energy deposition of the **middle two detectors** (Scin1, Scin2) as they are less prone to geometric corner-clipping effects than the outer detectors in this broader acceptance mode. Result: **29.85 MeV**.
       * *Decision:* Adopted the **Realistic (29.85 MeV)** value as it better represents the experimental trigger condition (which accepts angled tracks with slightly longer path lengths).
     * **Calculated Calibration Constants:**
       * **Ch1 (Top):** 272.5 mV → **0.1095 MeV/mV**
       * **Ch2 (Mid1):** 258.6 mV → **0.1154 MeV/mV**
       * **Ch3 (Mid2):** 264.1 mV → **0.1130 MeV/mV**
       * **Ch4 (Bot):** 293.8 mV → **0.1016 MeV/mV**
   * **Run 002 Analysis (1000 events):**
     * **Noise Filtering:** Implemented a threshold-based filter (rejecting events with Max Voltage > 30mV) to remove large positive noise excursions.
       * Result: **19/1000 events (1.9%) rejected** as noise. Confirmed rejected events were indeed artifacts.
     * **Landau Distributions:**
       * **Middle Detectors (Ch2, Ch3):** Observed clean, well-defined Landau peaks; successfully identified voltage MPVs.
       * **Top/Bottom Detectors (Ch1, Ch4):** Observed broader distributions with "clipping" effects, consistent with geometric acceptance limitations in a 4-fold coincidence setup.
     * **Data Acquisition (ADC-free):** Utilized the oscilloscope's **FastFrame** feature to capture 1000 events directly, successfully bypassing the need for an external ADC module.
     * **Power Supply Stability:** Channel 0 of the NDT1471 failed again in the morning but showed stability in the afternoon. Decided to proceed with all four detectors; Ch0 has remained stable throughout the afternoon acquisition.
     * **New Acquisition:** Started the **second 1000-event run** with **inner and outer detectors switched** to investigate systematic effects.
   * **Experimental Status:**
     * Validated analysis on a 10-event test run (`run001`).
     * **Started acquisition of a large run (1000 events)** to improve statistical significance.
   * **Waveform Analysis:**
     * Created `analysis/analyse_waveform.py` to process oscilloscope data (Tektronix CSV format).
     * Can parse multiple "FastFrame" events from a single CSV.
     * Generates waveform plots and peak amplitude statistics.
   * **Simulation & Analysis Upgrade:**
     * Cleaned up erroneous data from previous test runs (v00/v01).
     * Developed robust analysis tools for the 4-detector coincidence setup (`v0200`):
       * `analyse_v0200.py`: Performs Landau fits on energy deposition data to verify detector calibration.
       * `analyse_advanced.py`: Conducts detailed physics validation, including beam spot heatmaps, zenith angle reconstruction, and path length vs. energy correlation (dE/dx).
     * Successfully processed 100,000 simulated events.
     * Generated key validation plots:
       * **Calibration:** Verified distinct Landau peaks for all 4 detectors (~860 coincident events).
       * **Physics Check:** Confirmed "Corner Clipping" effect and validated the expected dE/dx behavior.
* **2026-01-18:**
   * Set up Git. Cleaned up messy runs.
   * Implemented logic for cosmic ray triggering.
     * N625: Signal duplication. There are four sections. Each sections have four inputs and four outputs. Outputs in each section is identical, the value is the sum of the inputs of the section.
     * N843: Discriminator. Converts signals to 0 or 1 depending on whether they meet the threshold voltage or not. (Takes negative voltage inputs)
     * N405: AND/OR. 
     * NDT1471: the power supply (used already for many weeks).
   * Setup
     * Each detector output is connected to N625, where the signal is duplicated. 
     * A copy of each signal is sent to the oscilliscope.
     * Another copy is sent to N843. Discriminator for each signal is set to -100mV.
     * The four outputs are then sent to N405. The AND gate takes in these four inputs, and creates one output.
     * AND gate output sent to oscilliscope auxilliary channel. Trigger is set to the AUX channel, with voltage -400mV.
   * Snags
     * CH0 of the power supply keeps failing to output the voltage (900V) and instead drops to 3V and displaying UnV warning.
     * Turned off and on the power supply. Works initially, but failed within a few minutes.
     * Switched power supply between DET01 and DET02, (CH0 and CH1). CH0 still failed. Ruled out detector problems.
     * Suspecting overheating of power supply. Decreased output of all four channels from 900V to 800V. 
     * Signal is still seen from the logic trigger despite PMT voltage reduction. Lowered discriminator to 50mV anyways.
     * CH0 still fails after a while.
* **2026-01-17:**
   * Identified another critical bug in the Geant4 simulation `v01_coincidence`. Due to the non-standard geometry orientation used, the cosmic rays should be entering from the y direction, instead of the z direction. Although that was included in the original code, it broke the cos^2 implementation, making all the particles enter parallel to the detector stack. (But then how would this explain the corner clipping effect seen previously with data from this run?)
   * Identified a bug in `v01_coincidence` simulation, the two detector labels were switched.
   * Fixed the geometry of the 2-detector stack (v01.1). In this version, the whole detector system is reoriented so that z is the direction of cosmic-rays (which matches the G4 standard)
   * Coded the geometry of the 4-detector stack (v02). The ROOT file now also records the precise Entry and Exit coordinates for every detector layer. This is imporant for a) Geometric Acceptance Verification, and b) "Golden Event" Filtering.
   * Simulated 100,000 events. Analysed the resulting ROOT files.
* **2026-01-16:**
   * Identified a critical bug in the Geant4 simulation `v01_coincidence` regarding the cosmic ray source definition. The source plane was incorrectly oriented and partially intersecting the geometry of the top detector. Correcting the source coordinates and rotation to ensure a proper flux through the detector stack.
* **2026-01-15:**
   * Assembled fourth and final detector with finalised design: (Outer scintillator casing v3 + Outer PMT casing v2 + Outer base casing v3 + Base 01)
   * Cosmic rays detected in all four detectors.
   * Switched the polarity of NDT1471's CH1 and CH2 to negative. (So that all four channels have negative polarity)
   * All four detectors placed in a vertical stack. Some cosmic ray signals detected simultaneously by all detectors.
* **2026-01-14:**
   * Printed outer casing for Base (v3) for the first and final time, applied bed adhesive for improved first-layer adhesion. (The cavity of the casing is slightly deeper ~2mm than v2, needed for Base 01, as it doesn't fit as tightly to the PMT as the other bases)
   * Assembled third detector with finalised design: (Outer scintillator casing v3 + Outer PMT casing v2 + Outer base casing v2 + Base 03)
     * Before assembly, the PMT and base was tested with LED signal. Signal was picked up in the oscilloscope, but not caused by LED. LED was definitely working (visible blue light when cranked up to 5V.) But PMT couldn't measure the signal when LED was at 2.8V, which had worked before. Unsure of what caused the issue.
     * Gambled on the assumption that PMT and base were working fine, and assembled the detector anyways. Cosmic rays were detected.
* **2026-01-13:**
   * Printed outer casing for Base (v2) for the second time, applied bed adhesive for improved first-layer adhesion.
   * Printed outer casing for Base (v2) for the third time, applied bed adhesive for improved first-layer adhesion.
   * Reassembled first detector with finalised design: (Outer scintillator casing v3 + Outer PMT casing v2 + Outer base casing v2 + Base 02)
   * Assembled second detector with finalised design: (Outer scintillator casing v3 + Outer PMT casing v2 + Outer base casing v2 + Base 04)
   * Detected cosmic ray signal passing through both detectors.
   * Submitted the Literature report, Thesis Proposal Assessment, and Thesis Progress report to the department.
* **2026-01-12:**
    * Printed outer casing for PMT (v2) for the fourth and final time, applied bed adhesive for improved first-layer adhesion.
    * Designed outer casing for Base (v2). Improvements: changed the design of the pilot holes to be compatible with 60mm M3 bolts.
    * Printed outer casing for Base (v2) for the first time, applied bed adhesive for improved first-layer adhesion.
    * Received the batch of 100 M3 bolts (60mm).
* **2026-01-11:**
    * Printed outer casing for PMT (v2) for the second time, applied bed adhesive for improved first-layer adhesion.
    * Printed outer casing for PMT (v2) for the third time, applied bed adhesive for improved first-layer adhesion.
* **2026-01-10:**
    * Designed outer casing for PMT (v2). Improvements: Increase in diameter for the PMT to go through (to account for the increase in diamter when PMT is wrapped in tin foil and electric tape.) Also, changed the pilot hole design to be compatible for 60mm M3 bolts.
    * Printed outer casing for PMT (v2) for the first time, applied bed adhesive for improved first-layer adhesion.
    * Completed thesis proposal presentation and assessment.
* **2026-01-09:**
    * Ordered a batch of 100 M3 bolts (60mm).
* **2026-01-08:**
    * Printed outer casing for Scintillator (v3) for the fourth (and final) time, applied bed adhesive for improved first-layer adhesion.
    * Literature review for undergraduate thesis proposal submitted to Prof Xiao.
* **2026-01-07:**
    * Printed outer casing for Scintillator (v3) for the third time, applied bed adhesive for improved first-layer adhesion.
* **2026-01-06:**
    * **Milestone: First "Full Detector" Prototype (Preview Version) assembled and functional.**
    * **Assembly Details:**
      * Integrated Scintillator casing (v3), PMT casing (v1), and Base casing (v1).
      * Used silicone gel at the scintillator-PMT interface for optical coupling.
      * Applied a light-tightness layer: Teflon tape on the scintillator's exposed face, followed by black electrical tape.
      * Wrapped the PMT in tin foil (for electromagnetic shielding/reflection) and secured with electrical tape.
      * *Note:* Casings have minor dimensional misalignments; used electrical tape for structural joining in this iteration.
      * *Note:* This iteration serves as a proof-of-concept; future versions will feature refined casing tolerances to eliminate the need for adhesive tape for structural integrity.
   * Printed outer casing for Scintillator (v3) for the second time, applied bed adhesive for improved first-layer adhesion.
   * **Logistics:** Teflon tape arrived.
   * **Troubleshooting (PMT Signal):** Partially resolved the "weird signal" issue from Jan 01.
      * *Investigation:* Ruled out oscilloscope and PMT hardware defects (swapped channels, tested with a 3rd fresh PMT).
      * *Solution:* Adjusted parameters per Zhou Yan's advice. Reduced LED drive from 5.5V to 2.8V and switched oscilloscope trigger from **LED Source** to **PMT Signal (Self-Trigger)**.
      * *Result:* Valid PMT pulses observed on the commercial base. Swapped back to custom bases (v2) and original PMTs; valid signals confirmed on all units.
      * *Conclusion:* Previous "square" signals and Over Current (OvC) were due to excessive LED driving voltage. PMTs are **not** burnt; PCBs are functional. True single-photoelectron signals are stochastic and require self-triggering to resolve at low voltages.
* **2026-01-05:**
    * Printed outer casing for Scintillator (v3), applied bed adhesive for improved first-layer adhesion.
    * Printed outer casing for Base (v1) applied bed adhesive for improved first-layer adhesion.
* **2026-01-04:**
    * **Simulation:** Successfully ran 10,000 event simulation (v01). Updated to accurate geometry (150x150x120mm), excluding Teflon/tape wrapping.
    * **Analysis:** Verified coincidence logic between stacked detectors. Observed "Corner Clipping" effect in the bottom detector.
    * **Hardware:** Printed outer casing for PMT (v1), applied bed adhesive for improved first-layer adhesion.
* **2026-01-03:** Printing outer casing for Scintillator (v2). But there were some curvature. Didn't apply 3D printing adhesive to the printing bed.
* **2026-01-02:**
    * **Milestone:** Produced the first clean Landau distribution plots via G4 simulation (v00).
    * Successfully ran first batch of 10,000 events (CSV data, 152.5x152.5x122.5mm scintillator size).
    * Printing outer casing for Scintillator (v1). But the casing dimensions were slightly off. Did not account for thickness of the teflon and electric tape.
* **2026-01-01:**
    * Testing of the 4 bases.
    * *Issue:* Anomalous signal detected across all four bases (even previously verified ones). Suspecting PMT defects, though switching PMTs did not resolve the issue. Neither did switching bases.

### December 2025
* **2025-12-31:**
    * *Happy New Year!*
* **2025-12-30:**
    * **Inventory:** 100x Pin Receptacles arrived.
    * Printed Socket housing v4 two times.
    * Soldered the remaining two PCB boards (Aligned the PCBv2 with Socket housing v4. Then crimped, and inserted, and soldered in place the 15 receptacles.)
    * Noticed that the bulkhead plate v2 was "slippery". The connectors slide when trying to connect/unconnect them.
    * Designed and printed bulkhead plate v3, with double D cut. (but faulty dimensions for bnc)
    * Designed and printed four bulkhead plates v4, with correct double D cut dimensions.
    * **Assembly:**
      * Ressembled first 2 bases. PCBv2 + Socket Housing v3 + Bulkhead Plate v4 + Inner casing v1 + 4x M2 50mm bolts and nuts.
      * Assembled last 2 bases. PCBv2 + Socket Housing v4 + Bulkhead Plate v4 + Inner casing v1 + 4x M2 50mm bolts and nuts.
    * Note: Base 1 doesn't plug into the PMT as well as the others, (due to how it was soldered). It doesn't plug in "as fully". Resulting in a slightly longer total length from end of base to the other end (PMT). Need to consider this when making outer casing.
* **2025-12-29:**
    * **Inventory:** 6x PETG Filament rolls and 50x M2 50mm bolts arrived.
    * Printed Socket housing v3 for the second time.
    * Printed Bulkhead Plate v1. (But realised that in reality the BNC connector was slightly smaller than SHV connector)
    * Designed and printed Bulkhead Plate v2. (Which has better hole sizes of each connector)
    * Printed Inner Casing v1. (A cylindrical shell. The "Shell" is about 5mm thick, with 4 pilot holes extruded all the way through to allow M2 bolts to go through.)
    * **Assembly:** Assembled base 1 and base 2 (Socket housing v3 + PCBv2 board + Inner casing v1 + bulkhead plate v2).
    * Tested both bases using Dark Box + Blue LED. Signal was observed across both Bases.
* **2025-12-27:**
    * Designed bulkhead plate v1
* **2025-12-26:**
    * PLA filament ran out. Plan to switch printing material from PLA to PETG. Ordered 6 rolls.
    * Ordered restock of receptacles (x100)
    * Ordered a batch of 50 M2 bolts (50mm).
    * Resigned Socket housing (v4), slightly increase diameter for the "donut hole" of the socket housing ring. Purpose was to avoid it from contacting with the solder bump, which will offset the alignment. (Not a major offset, did not affect base 1 and 2 a lot)
* **2025-12-25:** 🎄 *Merry Christmas!* Dark Box and LED test on (PCBv2Board2 + ZRJ's bulkhead plate). **Signal Detected.**
* **2025-12-24:**
    * Printed Socket housing (v1).
    * Printed Socket housing (v2), with a shorter housing height to match the length of the receptacle. Also increase socket size slightly, (to account for change of diameter when recaptacles are crimped)
    * Printed Socket housing (v3), with another increase of socket diameter over v2.
    * Crimped receptacles that were connected to Socket housing (v3) were soldered to PCBv2Board2.
* **2025-12-23:** Began independent design of Socket housing (v1).
* **2025-12-22:**
    * **Test:** Connected HV to first prototype. Conducted Dark box + LED test.
    * **Result:** Failure (Faulty connection on PCBv2Board1).
* **2025-12-20:**
    * New soldering set arrived.
    * Soldered BNC/SHV connectors.
    * **First Base prototype completed** (Hybrid design: My PCB + ZRJ mechanicals).
* **2025-12-19:**
    * BNC/SHV connectors arrived.
    * Old soldering set gave away. Ordered better soldering equipment.
* **2025-12-17:**
    * Soldered receptacles to ZRJ's housing.
    * Circuit confirmed functional with multimeter tests.
* **2025-12-12:** ZRJ finalised designs for bulkhead plate and socket housing. Printed out with PLA filament.
* **2025-12-06:** Batch of 50 pin receptacles arrived.
* **2025-12-03:** Voltage Divider PCB v2 arrived (x5).

### November 2025
* **2025-11-26:** Sent Voltage Divider PCB v2 for manufacturing.
* **2025-11-25:** Purchased initial batch of 50 pin receptacles.
* **2025-11-17:** Started design of Voltage Divider v2.
* **2025-11-12:** Voltage Divider PCB v1 arrived (x5).
* **2025-11-05:** Sent Voltage Divider PCB v1 for manufacturing.