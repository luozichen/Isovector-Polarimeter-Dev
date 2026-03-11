# v0400 Goal: SAMURAI Integration for Polarimeter Simulation

## Objective

Integrate the polarimeter simulation with the **smsimulator5.5** framework to:
1. Use the standardized SAMURAI infrastructure (beam handling, data format, physics lists)
2. Enable future coupling with the SAMURAI dipole magnet for fragment tracking
3. Maintain compatibility with the smsimulator analysis chain (TSimData, TClonesArray)

## Physics Setup

- **Beam**: 190 MeV/u deuteron (²H) → 380 MeV total kinetic energy
- **Target**: CH₂ (polyethylene) — proton-rich for (d,p) scattering
- **Physics List**: QGSP_BIC_XS — Binary Cascade model for intermediate energies, includes explicit cross-section data for light ions

## What's New vs v0300

| Feature | v0300 | v0400 |
|---------|-------|-------|
| Build system | CMake | GNUmakefile (smsimulator) |
| Physics list | QGSP_BIC_HP + Optical | QGSP_BIC_XS |
| Beam source | G4GeneralParticleSource | PrimaryGeneratorActionBasic |
| Hit format | Custom DET01Hit | TSimData (TClonesArray) |
| ROOT output | G4AnalysisManager | SimDataManager / RunActionBasic |
| Optical photons | Yes (scintillation) | No (hadronic focus) |
| SAMURAI magnet | No | Optional (DipoleConstruction) |
| NEBULA | No | Optional (NEBULAConstruction) |

## Next Steps

- [ ] Build and validate on remote server
- [ ] Test with pencil beam (example_Pencil.mac)
- [ ] Verify TSimData output in ROOT
- [ ] Enable dipole magnet and test fragment bending
- [ ] Compare polarimeter angular distributions with v0300 results
