#include "DET01DetectorConstruction.hh"

#include "G4Material.hh"
#include "G4Element.hh"
#include "G4NistManager.hh"

#include "G4Box.hh"
#include "G4Tubs.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4SystemOfUnits.hh"

#include "G4OpticalSurface.hh"
#include "G4LogicalBorderSurface.hh"
#include "G4LogicalSkinSurface.hh"
#include "G4LogicalVolumeStore.hh"
#include "G4SDManager.hh"
#include "DET01SensitiveDetector.hh"
#include "DET01ScintSD.hh"

DET01DetectorConstruction::DET01DetectorConstruction()
: G4VUserDetectorConstruction(), fPhotocathodeLogical(nullptr)
{
}

DET01DetectorConstruction::~DET01DetectorConstruction()
{
}

void DET01DetectorConstruction::DefineMaterials()
{
  G4NistManager* nist = G4NistManager::Instance();

  // Elements
  G4Element* H = nist->FindOrBuildElement("H");
  G4Element* C = nist->FindOrBuildElement("C");
  G4Element* Si = nist->FindOrBuildElement("Si");
  G4Element* O = nist->FindOrBuildElement("O");

  // 1. Air
  G4Material* air = nist->FindOrBuildMaterial("G4_AIR");
  
  // Optical properties of Air
  const G4int numEntries = 2;
  G4double photonEnergy[numEntries] = { 2.0*eV, 4.0*eV }; // 300-600nm range approx
  G4double rindexAir[numEntries]    = { 1.0, 1.0 };
  
  G4MaterialPropertiesTable* mptAir = new G4MaterialPropertiesTable();
  mptAir->AddProperty("RINDEX", photonEnergy, rindexAir, numEntries);
  air->SetMaterialPropertiesTable(mptAir);

  // 2. Scintillator (HND-S2 - Polystyrene based)
  // Polystyrene (C8H8)n -> Ratio H:C = 1:1
  G4Material* hnd_s2 = new G4Material("HND-S2", 1.05*g/cm3, 2);
  hnd_s2->AddElement(C, 1);
  hnd_s2->AddElement(H, 1);

  // Optical Properties
  // Peak Emission ~425 nm -> ~2.92 eV
  G4double rindexS2[numEntries]     = { 1.59, 1.59 };
  G4double absLengthS2[numEntries]  = { 380.*cm, 380.*cm }; // Keep standard long attenuation
  G4double scintEnergy[numEntries]  = { 2.92*eV, 2.92*eV }; 
  G4double scintFast[numEntries]    = { 1.0, 1.0 };
  
  G4MaterialPropertiesTable* mptS2 = new G4MaterialPropertiesTable();
  mptS2->AddProperty("RINDEX", photonEnergy, rindexS2, numEntries);
  mptS2->AddProperty("ABSLENGTH", photonEnergy, absLengthS2, numEntries);
  mptS2->AddProperty("SCINTILLATIONCOMPONENT1", scintEnergy, scintFast, numEntries);
  mptS2->AddConstProperty("SCINTILLATIONYIELD", 10000./MeV); 
  mptS2->AddConstProperty("RESOLUTIONSCALE", 1.0);
  mptS2->AddConstProperty("SCINTILLATIONTIMECONSTANT1", 2.6*ns); 
  mptS2->AddConstProperty("SCINTILLATIONRISETIME1", 0.7*ns);
  mptS2->AddConstProperty("SCINTILLATIONYIELD1", 1.0); 
  
  hnd_s2->SetMaterialPropertiesTable(mptS2);

  // 3. Borosilicate Glass (PMT Window)
  G4Material* glass = nist->FindOrBuildMaterial("G4_Pyrex_Glass");
  G4double rindexGlass[numEntries] = { 1.50, 1.50 }; // Approx
  G4double absGlass[numEntries]    = { 100.*cm, 100.*cm }; // Transparent
  
  G4MaterialPropertiesTable* mptGlass = new G4MaterialPropertiesTable();
  mptGlass->AddProperty("RINDEX", photonEnergy, rindexGlass, numEntries);
  mptGlass->AddProperty("ABSLENGTH", photonEnergy, absGlass, numEntries);
  glass->SetMaterialPropertiesTable(mptGlass);

  // 4. Optical Grease (Silicone)
  G4Material* grease = new G4Material("OpticalGrease", 1.06*g/cm3, 2);
  grease->AddElement(Si, 1);
  grease->AddElement(O, 2); // Very rough approx for Silicone chain backbone, adequate for optical dummy
  // Better: Polydimethylsiloxane (C2H6OSi)n
  // Let's stick to simple optical placeholders as composition doesn't affect optics much here, only RINDEX
  
  G4double rindexGrease[numEntries] = { 1.45, 1.45 }; // Range 1.4-1.5
  G4double absGrease[numEntries]    = { 100.*cm, 100.*cm }; 

  G4MaterialPropertiesTable* mptGrease = new G4MaterialPropertiesTable();
  mptGrease->AddProperty("RINDEX", photonEnergy, rindexGrease, numEntries);
  mptGrease->AddProperty("ABSLENGTH", photonEnergy, absGrease, numEntries);
  grease->SetMaterialPropertiesTable(mptGrease);

  // 5. Photocathode Material (Bi-Alkali) - Absorber
  // We model it as a thin metal that kills photons
  G4Material* bialkali = new G4Material("Bialkali", 2.0*g/cm3, 2);
  bialkali->AddElement(nist->FindOrBuildElement("K"), 2);
  bialkali->AddElement(nist->FindOrBuildElement("Sb"), 1);
  
  G4double rindexCathode[numEntries] = { 2.0, 2.0 }; // Complex index usually, simplify
  G4double absCathode[numEntries]    = { 1.0*nm, 1.0*nm }; // Absorbs immediately
  
  G4MaterialPropertiesTable* mptCathode = new G4MaterialPropertiesTable();
  mptCathode->AddProperty("RINDEX", photonEnergy, rindexCathode, numEntries);
  mptCathode->AddProperty("ABSLENGTH", photonEnergy, absCathode, numEntries);
  bialkali->SetMaterialPropertiesTable(mptCathode);

  // 6. Target Material (CH2)
  G4Material* ch2 = new G4Material("Target_CH2", 0.94*g/cm3, 2);
  ch2->AddElement(C, 1);
  ch2->AddElement(H, 2);
}

G4VPhysicalVolume* DET01DetectorConstruction::Construct()
{
  DefineMaterials();

  // Get Materials
  G4Material* air = G4Material::GetMaterial("G4_AIR");
  G4Material* scinMat = G4Material::GetMaterial("HND-S2");
  G4Material* glass = G4Material::GetMaterial("G4_Pyrex_Glass");
  G4Material* grease = G4Material::GetMaterial("OpticalGrease");
  G4Material* cathodeMat = G4Material::GetMaterial("Bialkali");
  G4Material* targetMat = G4Material::GetMaterial("Target_CH2");

  // --- Volumes ---

  // 1. World
  G4double worldSize = 4.0*m;
  G4Box* solidWorld = new G4Box("World", worldSize/2, worldSize/2, worldSize/2);
  G4LogicalVolume* logicWorld = new G4LogicalVolume(solidWorld, air, "World");
  G4VPhysicalVolume* physWorld = new G4PVPlacement(0, G4ThreeVector(), logicWorld, "World", 0, false, 0, true);

  // 2. CH2 Target
  // Size: 5cm x 5cm, 1cm thick
  G4double targetX = 5.0*cm;
  G4double targetY = 5.0*cm;
  G4double targetZ = 1.0*cm;
  G4Box* solidTarget = new G4Box("Target", targetX/2, targetY/2, targetZ/2);
  G4LogicalVolume* logicTarget = new G4LogicalVolume(solidTarget, targetMat, "Target");
  new G4PVPlacement(0, G4ThreeVector(0,0,0), logicTarget, "Target", logicWorld, false, 0, true);

  // Cylindrical Detector Dimensions
  // 40 mm diameter x 10 mm thick plastic scintillator disc
  G4double scinRad = 20.0*mm;
  G4double scinThick = 10.0*mm;  // This is the "depth" along the radial direction
  
  // Logical Volumes (Shared)
  G4Tubs* solidScin = new G4Tubs("Scintillator", 0., scinRad, scinThick/2, 0., 360.*deg);
  G4LogicalVolume* logicScin = new G4LogicalVolume(solidScin, scinMat, "Scintillator");

  // N2013 PMT: 29mm diameter
  G4double pmtDiam = 29.0*mm;
  G4double pmtRad = pmtDiam/2.0;
  G4double greaseThick = 0.1*mm;
  G4Tubs* solidGrease = new G4Tubs("Grease", 0., pmtRad, greaseThick/2, 0., 360.*deg);
  G4LogicalVolume* logicGrease = new G4LogicalVolume(solidGrease, grease, "Grease");
  
  G4double winThick = 2.0*mm;
  G4Tubs* solidWindow = new G4Tubs("PMTWindow", 0., pmtRad, winThick/2, 0., 360.*deg);
  G4LogicalVolume* logicWindow = new G4LogicalVolume(solidWindow, glass, "PMTWindow");
  
  G4double cathodeRad = 13.0*mm;  // N2013 effective cathode radius
  G4double cathodeThick = 0.1*mm; 
  G4Tubs* solidCathode = new G4Tubs("Photocathode", 0., cathodeRad, cathodeThick/2, 0., 360.*deg);
  fPhotocathodeLogical = new G4LogicalVolume(solidCathode, cathodeMat, "Photocathode");

  // Wrapping Surface
  // Use unified model with groundfrontpainted for curved G4Tubs surfaces.
  // (dielectric_LUT causes navigation errors on curved geometries)
  G4OpticalSurface* opTeflon = new G4OpticalSurface("TeflonSurface");
  opTeflon->SetType(dielectric_dielectric);
  opTeflon->SetModel(unified);
  opTeflon->SetFinish(groundfrontpainted);
  const G4int numEntries2 = 2;
  G4double pp2[numEntries2] = { 2.0*eV, 4.0*eV };
  G4double reflectivity[numEntries2] = { 0.95, 0.95 };
  G4MaterialPropertiesTable* mptTeflon = new G4MaterialPropertiesTable();
  mptTeflon->AddProperty("REFLECTIVITY", pp2, reflectivity, numEntries2);
  opTeflon->SetMaterialPropertiesTable(mptTeflon);

  // Polarimeter Array (Azimuthal Distribution)
  // 8 cylindrical detectors in two rings at different polar scattering angles.
  // Each ring has 4 detectors spaced 90 degrees in azimuth (Left, Up, Right, Down).
  //   Ring 0: theta = 20.0 deg, copyNo = 0..3
  //   Ring 1: theta = 30.0 deg, copyNo = 4..7
  //
  // Orientation: The flat circular face (local Z-plane) faces the target.
  // The PMT is attached to the back face, pointing radially outward.
  //
  // ROTATION: For a G4Tubs, the cylinder axis is along local Z.
  // We want local Z to point along the radial direction (r_hat).
  // Physical rotation: P = R_Z(phi) * R_Y(theta)
  // Geant4 passive:    R = P^T = R_Y(-theta) * R_Z(-phi)
  G4int nDetPerRing = 4;
  G4double phiStep = 90.0*deg;
  
  // Placement Parameters
  G4double distanceToTarget = 150.0*cm; // Distance from target to detector front face
  
  // Scattering angles for each ring
  const G4int nRings = 2;
  G4double scatteringAngles[nRings] = { 20.0*deg, 30.0*deg };
  
  // The scintillator center is at distanceToTarget + scinThick/2 along the
  // radial ray, since scinThick (10mm) is the depth along the radial direction.
  G4double rCenter = distanceToTarget + scinThick/2;

  // PMT radial distances (same for all detectors)
  G4double rGrease  = distanceToTarget + scinThick + greaseThick/2;
  G4double rWindow  = distanceToTarget + scinThick + greaseThick + winThick/2;
  G4double rCathode = distanceToTarget + scinThick + greaseThick + winThick + cathodeThick/2;

  for(G4int ring=0; ring<nRings; ring++) {
      G4double theta = scatteringAngles[ring];

      for(G4int i=0; i<nDetPerRing; i++) {
          G4double phi = i * phiStep;
          G4int copyNo = ring * nDetPerRing + i;
          
          // Rotation: local Z (cylinder axis) -> radial direction
          // Geant4 passive: R = R_Y(-theta) * R_Z(-phi)
          G4RotationMatrix* rotDet = new G4RotationMatrix();
          rotDet->rotateZ(-phi);
          rotDet->rotateY(-theta);
          
          // --- Positions (along radial ray) ---
          // Scintillator
          G4ThreeVector pos(0, 0, rCenter);
          pos.rotateY(theta);
          pos.rotateZ(phi);
          G4VPhysicalVolume* physScin = new G4PVPlacement(rotDet, pos, logicScin, "Scintillator", logicWorld, false, copyNo, true);
          new G4LogicalBorderSurface("ScinTeflonWrapper", physScin, physWorld, opTeflon);

          // Grease
          G4ThreeVector greasePos(0, 0, rGrease);
          greasePos.rotateY(theta);
          greasePos.rotateZ(phi);
          new G4PVPlacement(rotDet, greasePos, logicGrease, "Grease", logicWorld, false, copyNo, true);
          
          // Window
          G4ThreeVector winPos(0, 0, rWindow);
          winPos.rotateY(theta);
          winPos.rotateZ(phi);
          new G4PVPlacement(rotDet, winPos, logicWindow, "PMTWindow", logicWorld, false, copyNo, true);
          
          // Cathode
          G4ThreeVector cathodePos(0, 0, rCathode);
          cathodePos.rotateY(theta);
          cathodePos.rotateZ(phi);
          new G4PVPlacement(rotDet, cathodePos, fPhotocathodeLogical, "Photocathode", logicWorld, false, copyNo, true);
      }
  }

  return physWorld;
}

void DET01DetectorConstruction::ConstructSDandField()
{
  // 1. Photocathode SD (Counts Photons)
  if (fPhotocathodeLogical) {
      G4String sdName = "PmtSD";
      DET01SensitiveDetector* cathodeSD = new DET01SensitiveDetector(sdName, "HitsCollection");
      G4SDManager::GetSDMpointer()->AddNewDetector(cathodeSD);
      SetSensitiveDetector(fPhotocathodeLogical, cathodeSD);
  }

  // 2. Scintillator SD (Measures Energy Deposition)
  // We need to find the logical volume by name because we didn't store it in a member variable
  // Or simpler: We know the name is "Scintillator"
  G4LogicalVolume* scinLV = G4LogicalVolumeStore::GetInstance()->GetVolume("Scintillator");
  if (scinLV) {
      G4String scinSDName = "ScintSD";
      DET01ScintSD* scinSD = new DET01ScintSD(scinSDName, "ScintHitsCollection");
      G4SDManager::GetSDMpointer()->AddNewDetector(scinSD);
      SetSensitiveDetector(scinLV, scinSD);
  }
}
