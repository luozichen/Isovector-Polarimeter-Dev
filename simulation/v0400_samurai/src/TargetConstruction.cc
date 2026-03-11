// ============================================================
// TargetConstruction.cc
// Simple CH2 (polyethylene) target slab.
// ============================================================

#include "TargetConstruction.hh"

#include "G4Material.hh"
#include "G4Box.hh"
#include "G4LogicalVolume.hh"
#include "G4SystemOfUnits.hh"
#include "G4VisAttributes.hh"
#include "G4Colour.hh"

TargetConstruction::TargetConstruction()
: fSizeX(5.0*cm),
  fSizeY(5.0*cm),
  fSizeZ(1.0*cm)
{}

TargetConstruction::~TargetConstruction()
{}

G4LogicalVolume* TargetConstruction::ConstructSub()
{
  G4Material* targetMat = G4Material::GetMaterial("Target_CH2");

  G4Box* solidTarget = new G4Box("Target",
                                  fSizeX/2, fSizeY/2, fSizeZ/2);
  G4LogicalVolume* logicTarget = new G4LogicalVolume(solidTarget,
                                                      targetMat, "Target");

  // Visual attributes: Yellow for the target
  G4VisAttributes* targetVis = new G4VisAttributes(G4Colour(1.0, 1.0, 0.0, 0.7));
  targetVis->SetForceSolid(true);
  logicTarget->SetVisAttributes(targetVis);

  return logicTarget;
}
