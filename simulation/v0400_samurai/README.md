# v0400_samurai — SAMURAI Polarimeter Simulation

## Overview

This simulation extends the Isovector Polarimeter setup by integrating with the **smsimulator5.5** (smg4lib) framework. It uses the same polarimeter scintillator geometry as v0300 but leverages the smsimulator infrastructure for:

- **PrimaryGeneratorActionBasic**: macro-driven beam configuration
- **TSimData**: standardised ROOT hit format
- **SimDataManager**: automatic ROOT TTree output
- **DipoleConstruction**: SAMURAI dipole magnet with field maps (optional)
- **Physics**: QGSP_BIC_XS for intermediate-energy nuclear reactions

## Beam Configuration

- **Particle**: Deuteron (A=2, Z=1)
- **Energy**: 190 MeV/u → 380 MeV total kinetic energy
- **Target**: CH₂ (polyethylene), 5×5×1 cm³ at origin

## Detector Geometry

Two rings of 8 plastic scintillator bars each:

| Ring | θ (deg) | φ spacing | r (cm) | Bar size (mm³) |
|------|---------|-----------|--------|-----------------|
| 0    | 22.5    | 45°       | 150    | 120×150×150     |
| 1    | 30.0    | 45°       | 150    | 120×150×150     |

## Build

```bash
# On the remote server (enpg)
cd /data4/luozc25/github/Isovector-Polarimeter-Dev
source simulation/v0400_samurai/setup_env.sh
cd simulation/v0400_samurai
make
```

### Persistent shell setup (recommended)

If you open new terminals frequently, add this once to `~/.bashrc`:

```bash
# Isovector polarimeter environment (enpg)
if [ -f /data4/luozc25/github/Isovector-Polarimeter-Dev/simulation/v0400_samurai/setup_env.sh ]; then
  source /data4/luozc25/github/Isovector-Polarimeter-Dev/simulation/v0400_samurai/setup_env.sh
fi
```

The setup script is idempotent (safe to source multiple times), auto-detects a valid `geant4make.sh`, and exports all `smg4lib` paths required by `GNUmakefile`.

If your shell has stale exports from older setup scripts, reset and re-source:

```bash
unset SMSIMDIR SMSIMULATOR G4SMLIBDIR G4SMACTIONDIR G4SMCONSTRUCTIONDIR G4SMDATADIR G4SMPHYSICSDIR
source simulation/v0400_samurai/setup_env.sh
```

## Run

```bash
cd work
../bin/sim_polarimeter g4mac/examples/example_Pencil.mac
```

## Analysis

```bash
cd work
root -l rootlogon.C
root [0] .x macros/examples/analysis_example.cc("polarimeter_pencil0001.root")
```

## Geant4 Macro Commands

### Polarimeter Geometry
- `/polarimeter/geometry/Distance 150 cm` — target-to-detector distance
- `/polarimeter/geometry/AngleRing0 22.5 deg` — ring 0 scattering angle
- `/polarimeter/geometry/AngleRing1 30.0 deg` — ring 1 scattering angle
- `/polarimeter/geometry/NDetPerRing 8` — detectors per ring
- `/polarimeter/geometry/UseDipole true/false` — include SAMURAI dipole
- `/polarimeter/geometry/UseNEBULA true/false` — include NEBULA array

### Beam (from smg4lib)
- `/action/gun/Type Pencil|Gaus|Tree`
- `/action/gun/SetBeamParticleName deuteron`
- `/action/gun/Energy 380 MeV`
- See `g4mac/examples/` for full configurations.
