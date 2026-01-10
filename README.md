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
- [ ] System Integration: Complete the optical coupling of scintillators to PMTs and the final assembly of 4 detector units.
- [ ] Cosmic Ray Testing: Construct a cosmic ray telescope system to verify the detector's logic coincidence and long-term operational stability.
- [ ] Energy Calibration: Utilize the laboratory's Thorium source (Th-232) to perform precise energy calibration.

### Theoretical Derivation & Physics Simulation
- [ ] Polarization Derivation: Starting from quantum scattering theory, derive the analytical relationship between the deuteron-proton (d-p) elastic scattering cross-section and the beam's tensor polarization.
- [ ] Detection Simulation: Write code to simulate the scattering of the polarized deuteron beam on a methlyne target, and obtain the detector response, verifying the derivation and the rationality of the detector layout.
- [ ] Physics Verification: Using the ImQMD transport model to simulate the entire IVR experiment process, verifying the sensitivity of the experimental results to the beam polarization.
---

## 📅 Development Log

### January 2026
* **2026-01-10:**
    * Printed outer casing for PMT (v2) for the first time, with glue.
    * Completed thesis proposal presentation and assessment.
* **2026-01-08:**
    * Printed outer casing for Scintillator (v4) for the fourth (and final) time, with glue.
    * Literature review submitted for undergraduate thesis proposal
* **2026-01-07:**
    * Printed outer casing for Scintillator (v3) for the third time, with glue.
* **2026-01-06:**
    * **Milestone: First "Full Detector" Prototype (Preview Version) assembled and functional.**
    * **Assembly Details:**
      * Integrated Scintillator casing (v3), PMT casing (v1), and Base casing (v1).
      * Used silicone gel at the scintillator-PMT interface for optical coupling.
      * Applied a light-tightness layer: Teflon tape on the scintillator's exposed face, followed by black electrical tape.
      * Wrapped the PMT in tin foil (for electromagnetic shielding/reflection) and secured with electrical tape.
      * *Note:* Casings have minor dimensional misalignments; used electrical tape for structural joining in this iteration.
   * Printed outer casing for Scintillator (v3) for the second time, with glue.
   * **Logistics:** Teflon tape arrived.
   * **Troubleshooting (PMT Signal):** Partially resolved the "weird signal" issue from Jan 01.
      * *Investigation:* Ruled out oscilloscope and PMT hardware defects (swapped channels, tested with a 3rd fresh PMT).
      * *Solution:* Adjusted parameters per Zhou Yan's advice. Reduced LED drive from 5.5V to 2.8V and switched oscilloscope trigger from **LED Source** to **PMT Signal (Self-Trigger)**.
      * *Result:* Valid PMT pulses observed on the commercial base. Swapped back to custom bases (v2) and original PMTs; valid signals confirmed on all units.
      * *Conclusion:* Previous "square" signals and Over Current (OvC) were due to excessive LED driving voltage. PMTs are **not** burnt; PCBs are functional. True single-photoelectron signals are stochastic and require self-triggering to resolve at low voltages.
* **2026-01-05:**
    * Printed outer casing for Scintillator (v3) with glue.
    * Printed outer casing for Base (v1) with glue.
* **2026-01-04:**
    * **Simulation:** Successfully ran 10,000 event simulation. Updated to accurate geometry (150x150x120mm), excluding Teflon/tape wrapping.
    * **Analysis:** Verified coincidence logic between stacked detectors. Observed "Corner Clipping" effect in the bottom detector.
    * **Hardware:** Printed outer casing for PMT (v1) with glue.
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
    * **Fabrication:** Printed Socket housing, Bulkhead Plate, and Inner Casing.
    * **Assembly:** Fully assembled 2 bases.
* **2025-12-26:** Logistics update. Switched printing material from PLA to PETG. Ordered restock of receptacles and screws.
* **2025-12-25:** 🎄 *Merry Christmas!* Dark Box and LED test on (PCBv2Board2 + ZRJ's bulkhead plate). **Signal Detected.**
* **2025-12-24:** Printed Socket housing (v1). Connected to PCBv2Board2 and crimped receptacles.
* **2025-12-23:** Began independent design of Socket housing (v1).
* **2025-12-22:**
    * **Test:** Connected HV to first prototype. Conducted Dark box + LED test.
    * **Result:** Failure (Faulty connection on PCBv2Board1).
* **2025-12-20:** New soldering set arrived. Soldered BNC/SHV connectors. **First Base prototype completed** (Hybrid design: My PCB + ZRJ mechanicals).
* **2025-12-19:** Logistics: BNC/SHV connectors arrived. Ordered better soldering equipment.
* **2025-12-17:** Finished soldering receptacles to ZRJ's housing. Circuit confirmed functional.
* **2025-12-12:** ZRJ finalised designs for bulkhead plate and socket housing.
* **2025-12-06:** First batch of pin receptacles arrived.
* **2025-12-03:** Voltage Divider v2 arrived (x5).

### November 2025
* **2025-11-26:** Sent Voltage Divider v2 for manufacturing.
* **2025-11-25:** Purchased initial batch of pin receptacles.
* **2025-11-17:** Started design of Voltage Divider v2.
* **2025-11-12:** Voltage Divider v1 arrived (x5).
* **2025-11-05:** Sent Voltage Divider v1 for manufacturing.
