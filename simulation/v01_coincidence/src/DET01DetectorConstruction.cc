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

  // --- Volumes ---

  // 1. World
  G4double worldSize = 2.0*m;
  G4Box* solidWorld = new G4Box("World", worldSize/2, worldSize/2, worldSize/2);
  G4LogicalVolume* logicWorld = new G4LogicalVolume(solidWorld, air, "World");
  G4VPhysicalVolume* physWorld = new G4PVPlacement(0, G4ThreeVector(), logicWorld, "World", 0, false, 0, true);

  // Detector Dimensions
  // 120 mm x 150 mm x 150 mm
  // X = 120, Y = 150, Z = 150
  G4double scinX = 120.0*mm;
  G4double scinY = 150.0*mm;
  G4double scinZ = 150.0*mm;
  
  // Logical Volumes (Shared)
  G4Box* solidScin = new G4Box("Scintillator", scinX/2, scinY/2, scinZ/2);
  G4LogicalVolume* logicScin = new G4LogicalVolume(solidScin, scinMat, "Scintillator");

  G4double pmtDiam = 51.0*mm;
  G4double pmtRad = pmtDiam/2.0;
  G4double greaseThick = 0.1*mm;
  G4Tubs* solidGrease = new G4Tubs("Grease", 0., pmtRad, greaseThick/2, 0., 360.*deg);
  G4LogicalVolume* logicGrease = new G4LogicalVolume(solidGrease, grease, "Grease");
  
  G4double winThick = 2.0*mm;
  G4Tubs* solidWindow = new G4Tubs("PMTWindow", 0., pmtRad, winThick/2, 0., 360.*deg);
  G4LogicalVolume* logicWindow = new G4LogicalVolume(solidWindow, glass, "PMTWindow");
  
  G4double cathodeRad = 23.0*mm;
  G4double cathodeThick = 0.1*mm; 
  G4Tubs* solidCathode = new G4Tubs("Photocathode", 0., cathodeRad, cathodeThick/2, 0., 360.*deg);
  fPhotocathodeLogical = new G4LogicalVolume(solidCathode, cathodeMat, "Photocathode");

  // Wrapping Surface
  G4OpticalSurface* opTeflon = new G4OpticalSurface("TeflonSurface");
  opTeflon->SetType(dielectric_LUT);
  opTeflon->SetModel(unified);
  opTeflon->SetFinish(groundteflonair);

  // Stacking Loop
  G4int nDetectors = 2;
  G4double gap = 10.0*mm;
  G4double stackHeight = nDetectors * scinY + (nDetectors - 1) * gap;
  G4double startY = -stackHeight/2 + scinY/2;

  G4RotationMatrix* rot = new G4RotationMatrix();
  rot->rotateY(90.*deg); 

  for(G4int i=0; i<nDetectors; i++) {
      G4double posY = startY + i * (scinY + gap);
      G4ThreeVector pos(0, posY, 0);
      
      // Scintillator
      G4VPhysicalVolume* physScin = new G4PVPlacement(0, pos, logicScin, "Scintillator", logicWorld, false, i, true);
      
      // Apply Wrapping to this specific instance boundary
      new G4LogicalBorderSurface("ScinTeflonWrapper", physScin, physWorld, opTeflon);

      // Attach PMT Assembly (Relative to Scintillator center)
      // PMT is on +X face. Global X = +scinX/2. Global Y = posY.
      G4double pmtAxisPos = scinX/2;
      
      // Grease
      G4ThreeVector greasePos(pmtAxisPos + greaseThick/2, posY, 0);
      new G4PVPlacement(rot, greasePos, logicGrease, "Grease", logicWorld, false, i, true);
      
      // Window
      G4ThreeVector winPos(pmtAxisPos + greaseThick + winThick/2, posY, 0);
      new G4PVPlacement(rot, winPos, logicWindow, "PMTWindow", logicWorld, false, i, true);
      
      // Cathode
      G4ThreeVector cathodePos(pmtAxisPos + greaseThick + winThick + cathodeThick/2, posY, 0);
      new G4PVPlacement(rot, cathodePos, fPhotocathodeLogical, "Photocathode", logicWorld, false, i, true);
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
