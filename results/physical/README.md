# Experimental Run Log (Physical Data)

This document tracks the parameters and configurations for each experimental run captured by the detector system.

## Global Parameters (Runs 001 - 012)
- **Operating Voltage:** 800V (All detectors)
- **Coincidence Logic:** 4-fold AND (All 4 detectors must fire simultaneously)
- **Oscilloscope Scale:** 100 mV/div (Vertical)
- **Output Data:** Raw waveforms for all 4 detectors (.wfm format)
- **FastFrame Events:** 1000 waveforms per run (unless specified)
- **Position Mapping:** Config `ABCD` means:
  - **A:** Top Position
  - **B:** Middle 1 Position
  - **C:** Middle 2 Position
  - **D:** Bottom Position

---

## Run List

### Run 001
- **Status:** Test Run
- **Config:** 1234
- **Discriminator:** 50 mV
- **Events:** 10
- **Note:** Initial system verification.

### Calibration & Jitter Group (Runs 002 - 007)
*Objective: Permute detector positions to acquire "Golden Pair" data (detectors in middle positions) for all 4 units.*

- **Run 002:** Config 1234, Disc 50 mV.
- **Run 003:** Config 2143, Disc 50 mV. (Switched inner/outer to check systematics)
- **Run 004:** Config 2134, Disc 50 mV. (Golden: Det 1 & Det 3)
- **Run 005:** Config 3124, Disc 50 mV. (Golden: Det 1 & Det 2)
- **Run 006:** Config 1243, Disc 50 mV. (Golden: Det 2 & Det 4)
- **Run 007:** Config 1342, Disc 50 mV. (Golden: Det 3 & Det 4)

---

## Source Investigation Group

### Run 008
- **Config:** 1342
- **Discriminator:** 50 mV
- **Source:** Thorium-232 (Directly above Top detector)
- **Note:** First Thorium investigation. No noticeable energy shift observed at 50mV threshold.

### Run 009
- **Config:** 1342
- **Discriminator:** 15 mV
- **Source:** Thorium-232
- **Note:** Lowered threshold to search for low-energy gamma interactions.

### Run 010
- **Config:** 1342
- **Discriminator:** 15 mV
- **Source:** None (Background)
- **Note:** Control run for 15mV Thorium study.

### Run 011
- **Config:** 1342
- **Discriminator:** 5 mV
- **Source:** Thorium-232
- **Note:** Minimal threshold run. Revealed unexplained 2-3mV peak (likely SPE/Accidental coincidences).

### Run 012
- **Config:** 1342
- **Discriminator:** 5 mV
- **Source:** None (Background)
- **Note:** Control run for 5mV Thorium study. Verified Thorium signal excess at low energy.

### Run 013
- **Config:** Det 1 only (Single Fold)
- **Discriminator:** 10 mV
- **Events:** 10,000
- **Source:** None (Background)
- **Note:** Transition to single-detector triggering for source calibration study.

### Run 014
- **Config:** Det 1 only (Single Fold)
- **Discriminator:** 10 mV
- **Events:** 10,000
- **Source:** Thorium-232 (Directly above Det 1)
- **Note:** High-statistics Thorium run for comparison with Run 013.
