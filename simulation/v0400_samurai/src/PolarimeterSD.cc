// ============================================================
// PolarimeterSD.cc
// Sensitive detector for polarimeter scintillator bars.
// Records hit data into smsimulator TSimData format via
// the SimDataManager singleton.
// ============================================================

#include <map>
#include <iostream>

#include "PolarimeterSD.hh"

// Geant4
#include "G4Step.hh"
#include "G4HCofThisEvent.hh"
#include "G4TouchableHistory.hh"
#include "G4Track.hh"
#include "G4SystemOfUnits.hh"
#include "G4ios.hh"

// smg4lib/data
#include "SimDataManager.hh"
using std::ostream;
using std::istream;
#include "TSimData.hh"

// ROOT
#include "TClonesArray.h"

PolarimeterSD::PolarimeterSD(const G4String& name)
: G4VSensitiveDetector(name),
  fDetectorName("PolarimeterSimData")
{
  // NOTE:
  // Older smsimulator/smg4lib versions do not provide
  // SimDataManager::RegistSimDataArray(...). Keep constructor minimal
  // and rely on existing framework-side array registration.
}

PolarimeterSD::~PolarimeterSD()
{}

void PolarimeterSD::Initialize(G4HCofThisEvent*)
{
  // Access the manager and clear the array for the new event
  SimDataManager* simDataManager = SimDataManager::GetSimDataManager();
  TClonesArray* simDataArray = simDataManager->FindSimDataArray("PolarimeterSimData");
  if (simDataArray) simDataArray->Clear("C");
}

G4bool PolarimeterSD::ProcessHits(G4Step* step, G4TouchableHistory*)
{
  // Get energy deposit
  G4double edep = step->GetTotalEnergyDeposit();

  // Skip zero-energy steps
  if (edep <= 0.) return false;

  // Get step information
  G4Track* track = step->GetTrack();
  G4StepPoint* preStep  = step->GetPreStepPoint();
  G4StepPoint* postStep = step->GetPostStepPoint();

  // Detector copy number identifies which scintillator bar
  G4int detID = preStep->GetTouchable()->GetCopyNumber();

  // Position (mid-step)
  G4ThreeVector pos = 0.5 * (preStep->GetPosition() + postStep->GetPosition());

  // Time
  G4double time = preStep->GetGlobalTime();

  // Particle info
  G4int trackID   = track->GetTrackID();
  G4int parentID  = track->GetParentID();
  G4int pdgCode   = track->GetDefinition()->GetPDGEncoding();
  G4double charge = track->GetDefinition()->GetPDGCharge();
  G4double mass   = track->GetDefinition()->GetPDGMass();

  // Momentum
  G4ThreeVector mom = preStep->GetMomentum();

  // Fill TSimData
  SimDataManager* simDataManager = SimDataManager::GetSimDataManager();
  TClonesArray* simDataArray = simDataManager->FindSimDataArray("PolarimeterSimData");

  if (simDataArray) {
    Int_t nhits = simDataArray->GetEntries();
    TSimData* simData = new ((*simDataArray)[nhits]) TSimData();

    simData->fDetectorName = fDetectorName;
    simData->fID        = detID;
    simData->fTrackID      = trackID;
    simData->fParentID     = parentID;
    simData->fPDGCode      = pdgCode;
    simData->fCharge       = charge;
    simData->fMass         = mass / MeV;  // Store in MeV

    simData->fPrePosition.SetXYZ(preStep->GetPosition().x() / mm,
                                  preStep->GetPosition().y() / mm,
                                  preStep->GetPosition().z() / mm);

    simData->fPostPosition.SetXYZ(postStep->GetPosition().x() / mm,
                                   postStep->GetPosition().y() / mm,
                                   postStep->GetPosition().z() / mm);

    simData->fPreMomentum.SetPxPyPzE(mom.x() / MeV,
                                     mom.y() / MeV,
                                     mom.z() / MeV,
                                     preStep->GetTotalEnergy() / MeV);

    simData->fEnergyDeposit = edep / MeV;
    simData->fPreTime       = time / ns;
  }

  return true;
}

void PolarimeterSD::EndOfEvent(G4HCofThisEvent*)
{
  // Data is already stored in SimDataManager's TClonesArray.
  // RunActionBasic / EventActionBasic handle writing to ROOT TTree.
}
