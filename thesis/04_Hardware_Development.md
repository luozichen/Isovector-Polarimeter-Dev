# Chapter 4: Detector Hardware Development

## 4.1 Overview
To experimentally verify the simulation results, a modular scintillator-based polarimeter prototype was designed and constructed. The system consists of four identical detection units, arranged in a vertical stack to form a cosmic ray telescope. This chapter details the iterative engineering process of the mechanical structure, the custom electronics, and the final system integration.

## 4.2 Scintillator & PMT System

### 4.2.1 Component Selection
*   **Scintillator:** HND-S2 plastic scintillator (120mm x 150mm x 150mm). Chosen for its fast rise time and durability.
*   **Photomultiplier Tube (PMT):** 2-inch PMTs were selected for readout.
*   **Optical Coupling:** To maximize light collection, a silicone optical grease layer (approx. 0.1mm) was applied between the scintillator light guide and the PMT face.

### 4.2.2 Light Tightness
Ensuring a light-tight environment is critical for single-photon sensitivity. The wrapping procedure evolved through testing:
1.  **Reflective Layer:** The scintillator was wrapped in Teflon tape to act as a diffuse reflector.
2.  **Shielding:** A layer of tin foil was wrapped around the PMT to provide electromagnetic shielding and additional light reflection.
3.  ** sealing:** The entire assembly was wrapped in black electrical tape.

## 4.3 Mechanical Design (3D Printing)

The outer casing was designed in CAD and manufactured using 3D printing (PLA and PETG). The design underwent three major iterations to address tolerance and structural issues.

*   **Version 1 (Prototype):** Basic cylindrical shell. Failed due to lack of tolerance for tape thickness.
*   **Version 2 (Intermediate):** Adjusted PMT diameter. Added pilot holes for M3 bolts. Used for the first successful dark-box test.
*   **Version 3 (Final Production):**
    *   **Scintillator Casing:** Dimensions expanded to 152.5mm to accommodate Teflon/Tape wrapping.
    *   **Base Casing:** Deepened cavity by 2mm to fit the custom "Base 01" PCB stack.
    *   **Assembly:** Features "Double D" cutouts on the bulkhead plate for secure BNC/SHV connector mounting.
    *   **Material:** Printed with bed adhesive to prevent warping (a major issue in V1/V2).

## 4.4 Electronics: Voltage Divider Design

A custom voltage divider PCB was designed to distribute the High Voltage (HV) across the PMT dynodes.

### 4.4.1 PCB Iterations
*   **v1 (Nov 2025):** Initial design. Manufactured x5. Functional but lacked robust mechanical mounting points.
*   **v2 (Dec 2025):** Improved layout. Added dedicated mounting holes for the 3D-printed socket housing.
    *   **Socket Housing:** A custom 3D-printed "donut" ring (v4) aligns the PCB with the PMT pins.
    *   **Connectors:** High-quality SHV (Safe High Voltage) and BNC connectors were soldered to the bulkhead plate.

### 4.4.2 Power Supply & Logic
*   **HV Supply:** CAEN NDT1471. Operated at approximately -800V to -900V.
    *   *Issue:* Channel 0 exhibited instability (voltage drops/over-current) at 900V. Resolved by lowering the operating voltage to 800V for stable coincidence runs.
*   **Signal Processing:**
    *   **N625:** Linear Fan-in/Fan-out (Signal Duplication).
    *   **N843:** Constant Threshold Discriminator. Threshold set to -30mV to reject thermal noise.
    *   **N405:** Logic Unit (AND Gate) to establish 4-fold coincidence.

## 4.5 System Integration
The four detectors (Det 1-4) were assembled into a vertical stack structure.
*   **Alignment:** Detectors are aligned along the vertical Z-axis.
*   **Trigger Logic:** The system triggers only when a cosmic ray muon traverses all four detectors simultaneously (4-fold coincidence). This selects for high-energy, vertical muons, providing a "clean" particle beam for calibration.
