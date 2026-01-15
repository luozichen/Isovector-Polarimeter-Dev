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
- [ ] Energy Calibration: Utilize the laboratory's Thorium source (Th-232) to perform precise energy calibration.

### Theoretical Derivation & Physics Simulation
- [ ] Polarization Derivation: Starting from quantum scattering theory, derive the analytical relationship between the deuteron-proton (d-p) elastic scattering cross-section and the beam's tensor polarization.
- [ ] Detection Simulation: Write code to simulate the scattering of the polarized deuteron beam on a methlyne target, and obtain the detector response, verifying the derivation and the rationality of the detector layout.
- [ ] Physics Verification: Using the ImQMD transport model to simulate the entire IVR experiment process, verifying the sensitivity of the experimental results to the beam polarization.
---

## 📅 Development Log

### January 2026
* **2026-01-15:**
   * Assembled fourth and final detector with finalised design: (Outer scintillator casing v4 + Outer PMT casing v2 + Outer base casing v3 + Base 01)
   * Cosmic rays detected in all four detectors.
* **2026-01-14:**
   * Printed outer casing for Base (v3) for the first and final time, applied bed adhesive for improved first-layer adhesion. (This casing is needed for Base 01, as it doesn't fit as tightly to the PMT as the other bases)
   * Assembled third detector with finalised design: (Outer scintillator casing v4 + Outer PMT casing v2 + Outer base casing v2 + Base 03)
     * Before assembly, the PMT and base was tested with LED signal. Signal was picked up in the oscilloscope, but not caused by LED. LED was definitely working (visible blue light when cranked up to 5V.) But PMT couldn't measure the signal when LED was at 2.8V, which had worked before. Unsure of what caused the issue.
     * Gambled on the assumption that PMT and base were working fine, and assembled the detector anyways. Cosmic rays were detected.
* **2026-01-13:**
   * Printed outer casing for Base (v2) for the second time, applied bed adhesive for improved first-layer adhesion.
   * Printed outer casing for Base (v2) for the third time, applied bed adhesive for improved first-layer adhesion.
   * Reassembled first detector with finalised design: (Outer scintillator casing v4 + Outer PMT casing v2 + Outer base casing v2 + Base 02)
   * Assembled second detector with finalised design: (Outer scintillator casing v4 + Outer PMT casing v2 + Outer base casing v2 + Base 04)
   * Detected cosmic ray signal passing through both detectors.
* **2026-01-12:**
    * Printed outer casing for PMT (v2) for the fourth and final time, applied bed adhesive for improved first-layer adhesion.
    * Printed outer casing for Base (v2) for the first time, applied bed adhesive for improved first-layer adhesion.
    * Received the batch of 100 M3 bolts (60mm).
* **2026-01-11:**
    * Printed outer casing for PMT (v2) for the second time, applied bed adhesive for improved first-layer adhesion.
    * Printed outer casing for PMT (v2) for the third time, applied bed adhesive for improved first-layer adhesion.
* **2026-01-10:**
    * Printed outer casing for PMT (v2) for the first time, applied bed adhesive for improved first-layer adhesion.
    * Completed thesis proposal presentation and assessment.
* **2026-01-09:**
    * Ordered a batch of 100 M3 bolts (60mm)
* **2026-01-08:**
    * Printed outer casing for Scintillator (v4) for the fourth (and final) time, applied bed adhesive for improved first-layer adhesion.
    * Literature review submitted for undergraduate thesis proposal
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
    * **Simulation:** Successfully ran 10,000 event simulation. Updated to accurate geometry (150x150x120mm), excluding Teflon/tape wrapping.
    * **Analysis:** Verified coincidence logic between stacked detectors. Observed "Corner Clipping" effect in the bottom detector.
    * **Hardware:** Printed outer casing for PMT (v1), applied bed adhesive for improved first-layer adhesion.
* **2026-01-03:** Printing outer casing for Scintillator (v2).
* **2026-01-02:**
    * **Milestone:** Produced the first clean Landau distribution plots.
    * Successfully ran first batch of 10,000 events (CSV data, 152.5x152.5x122.5mm scintillator size).
    * Printing outer casing for Scintillator (v1).
* **2026-01-01:**
    * Testing of the 4 bases.
    * *Issue:* Anomalous signal detected across all four bases (even previously verified ones). Suspecting PMT defects, though switching PMTs did not resolve the issue. Neither did switching bases.

### December 2025
* **2025-12-30:**
    * **Inventory:** 100x Pin Receptacles arrived.
    * **Assembly:** Fully assembled the 2 remaining bases (4 total). Config: Custom PCB + Custom Socket Housing + Custom Bulkhead + M2 50mm screws.
* **2025-12-29:**
    * **Inventory:** 6x PETG Filament rolls and 50x M2 50mm screws arrived.
    * Printed Socket housing
    * Printed Bulkhead Plate
    * Printed Inner Casing.
    * **Assembly:** Fully assembled 2 bases.
* **2025-12-26:**
    * PLA filament ran out. Plan to switch printing material from PLA to PETG. Ordered 6 rolls.
    * Ordered restock of receptacles (x100)
    * Ordered a batch of 50 M2 bolts (50mm).
* **2025-12-25:** 🎄 *Merry Christmas!* Dark Box and LED test on (PCBv2Board2 + ZRJ's bulkhead plate). **Signal Detected.**
* **2025-12-24:**
    * Printed Socket housing (v1).
    * Crimped receptacles that were connected to Socket housing (v1) were soldered to PCBv2Board2.
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
