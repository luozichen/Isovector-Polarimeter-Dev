// ============================================================
// PolarimeterDetectorConstruction.cc
// Assembles the full SAMURAI polarimeter geometry:
//   - World volume
//   - CH2 target at origin
//   - SAMURAI dipole magnet (optional, from smg4lib)
//   - NEBULA neutron array (optional, from smg4lib)
//   - Polarimeter scintillator ring (custom)
// ============================================================

#include "PolarimeterDetectorConstruction.hh"
#include "PolarimeterDetectorConstructionMessenger.hh"
#include "PolarimeterSD.hh"
#include "TargetConstruction.hh"

// Geant4
#include "G4Material.hh"
#include "G4NistManager.hh"
#include "G4Box.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4SystemOfUnits.hh"
#include "G4RotationMatrix.hh"
#include "G4ThreeVector.hh"
#include "G4SDManager.hh"
#include "G4VisAttributes.hh"
#include "G4Colour.hh"

// smg4lib/construction (optional components)
#include "DipoleConstruction.hh"
#include "DipoleConstructionMessenger.hh"
#include "NEBULAConstruction.hh"
#include "NEBULAConstructionMessenger.hh"
#include "ExitWindowC1Construction.hh"

PolarimeterDetectorConstruction::PolarimeterDetectorConstruction()
: G4VUserDetectorConstruction(),
  fMessenger(nullptr),
  fTargetDistance(150.0*cm),
  fAngleRing0(22.5*deg),
  fAngleRing1(30.0*deg),
  fNDetPerRing(8),
  fUseDipole(true),
  fUseNEBULA(false),
  fPolarimeterScinLogical(nullptr)
{
  fMessenger = new PolarimeterDetectorConstructionMessenger(this);
}

PolarimeterDetectorConstruction::~PolarimeterDetectorConstruction()
{
  delete fMessenger;
}

void PolarimeterDetectorConstruction::DefineMaterials()
{
  G4NistManager* nist = G4NistManager::Instance();

  // Air
  nist->FindOrBuildMaterial("G4_AIR");

  // Plastic scintillator (BC-408 equivalent, polyvinyltoluene-based)
  // Approx (C9H10)n, density ~1.032 g/cm3
  G4Element* H = nist->FindOrBuildElement("H");
  G4Element* C = nist->FindOrBuildElement("C");

  G4Material* scintMat = new G4Material("PlasticScintillator",
                                         1.032*g/cm3, 2);
  scintMat->AddElement(C, 9);
  scintMat->AddElement(H, 10);

  // CH2 target (polyethylene)
  G4Material* ch2 = new G4Material("Target_CH2", 0.94*g/cm3, 2);
  ch2->AddElement(C, 1);
  ch2->AddElement(H, 2);

  // Vacuum (for beamline if needed)
  nist->FindOrBuildMaterial("G4_Galactic");
}

G4VPhysicalVolume* PolarimeterDetectorConstruction::Construct()
{
  DefineMaterials();

  // --- Materials ---
  G4Material* air       = G4Material::GetMaterial("G4_AIR");
  G4Material* scintMat  = G4Material::GetMaterial("PlasticScintillator");
  G4Material* targetMat = G4Material::GetMaterial("Target_CH2");

  // ===============================================
  // 1. World Volume
  // ===============================================
  G4double worldSize = 10.0*m;
  G4Box* solidWorld = new G4Box("World",
                                worldSize/2, worldSize/2, worldSize/2);
  G4LogicalVolume* logicWorld = new G4LogicalVolume(solidWorld, air, "World");
  logicWorld->SetVisAttributes(G4VisAttributes::GetInvisible());

  G4VPhysicalVolume* physWorld = new G4PVPlacement(
      0, G4ThreeVector(), logicWorld, "World", 0, false, 0, true);

  // ===============================================
  // 2. CH2 Target at Origin
  // ===============================================
  TargetConstruction targetBuilder;
  G4LogicalVolume* logicTarget = targetBuilder.ConstructSub();

  new G4PVPlacement(0, G4ThreeVector(0, 0, 0),
                    logicTarget, "Target", logicWorld, false, 0, true);

  // ---> SANITY TARGET <---

  // ===============================================
  // 3. SAMURAI Dipole Magnet (optional)
  // ===============================================
  if (fUseDipole) {
    // The SAMURAI dipole is centered at z ~ 3.5 m downstream
    // with field map. DipoleConstruction handles the full geometry
    // including yoke, vacuum chamber, and field.
    // Configuration is done via /samurai/geometry/Dipole/ commands.
    DipoleConstruction dipoleBuilder;
    G4LogicalVolume* logicDipole = dipoleBuilder.ConstructSub();
    if (logicDipole) {
      // Standard SAMURAI position:
      // Dipole center at z = 3564 mm (from target position)
      new G4PVPlacement(0, G4ThreeVector(0, 0, 3564.0*mm),
                        logicDipole, "Dipole", logicWorld, false, 0, true);
    }
  }

  // ===============================================
  // 4. Polarimeter Scintillator Ring
  // ===============================================
  // Detector dimensions: 120 mm depth x 150 mm x 150 mm face
  // Same geometry as v0300
  G4double scinDepth  = 120.0*mm;  // along radial direction (local X)
  G4double scinWidth  = 150.0*mm;  // transverse (local Y)
  G4double scinHeight = 150.0*mm;  // transverse (local Z)

  G4Box* solidScin = new G4Box("PolarimeterScin",
                                scinDepth/2, scinWidth/2, scinHeight/2);
  fPolarimeterScinLogical = new G4LogicalVolume(solidScin, scintMat,
                                                 "PolarimeterScin_log");

  // Visual attributes: Cyan for polarimeter bars
  G4VisAttributes* scinVis = new G4VisAttributes(G4Colour(0.0, 0.8, 0.8, 0.5));
  scinVis->SetForceSolid(true);
  fPolarimeterScinLogical->SetVisAttributes(scinVis);

  // Place detectors in two rings
  G4double phiStep = 360.0*deg / fNDetPerRing;
  G4double rCenter = fTargetDistance + scinDepth/2;

  const G4int nRings = 2;
  G4double scatteringAngles[nRings] = { fAngleRing0, fAngleRing1 };

  for (G4int ring = 0; ring < nRings; ring++) {
    G4double theta = scatteringAngles[ring];

    for (G4int i = 0; i < fNDetPerRing; i++) {
      G4double phi = i * phiStep;
      G4int copyNo = ring * fNDetPerRing + i;

      // Rotation: map local +X to radial direction
      // Physical rotation: P = R_Z(phi) * R_Y(-(90-theta))
      // Geant4 passive:    R = P^T = R_Y(90-theta) * R_Z(-phi)
      G4RotationMatrix* rot = new G4RotationMatrix();
      rot->rotateZ(-phi);
      rot->rotateY(90.*deg - theta);

      // Position: radial center at (rCenter) along the ray
      G4ThreeVector pos(0, 0, rCenter);
      pos.rotateY(theta);
      pos.rotateZ(phi);

      new G4PVPlacement(rot, pos, fPolarimeterScinLogical,
                        "PolarimeterScin", logicWorld, false, copyNo, true);
    }
  }

  return physWorld;
}

void PolarimeterDetectorConstruction::ConstructSDandField()
{
  // Register PolarimeterSD for the scintillator logical volume
  if (fPolarimeterScinLogical) {
    G4String sdName = "PolarimeterSD";
    PolarimeterSD* polSD = new PolarimeterSD(sdName);
    G4SDManager::GetSDMpointer()->AddNewDetector(polSD);
    SetSensitiveDetector(fPolarimeterScinLogical, polSD);
  }
}
