// ============================================================
// PolarimeterDetectorConstructionMessenger.cc
// UI commands for configuring polarimeter geometry at runtime
// ============================================================

#include "PolarimeterDetectorConstructionMessenger.hh"
#include "PolarimeterDetectorConstruction.hh"

#include "G4UIdirectory.hh"
#include "G4UIcmdWithADoubleAndUnit.hh"
#include "G4UIcmdWithAnInteger.hh"
#include "G4UIcmdWithABool.hh"

PolarimeterDetectorConstructionMessenger::PolarimeterDetectorConstructionMessenger(
    PolarimeterDetectorConstruction* det)
: G4UImessenger(),
  fDetector(det)
{
  fDir = new G4UIdirectory("/polarimeter/geometry/");
  fDir->SetGuidance("Polarimeter detector geometry configuration.");

  fDistanceCmd = new G4UIcmdWithADoubleAndUnit("/polarimeter/geometry/Distance", this);
  fDistanceCmd->SetGuidance("Set target-to-polarimeter front face distance.");
  fDistanceCmd->SetParameterName("Distance", false);
  fDistanceCmd->SetDefaultUnit("cm");
  fDistanceCmd->SetUnitCategory("Length");
  fDistanceCmd->AvailableForStates(G4State_PreInit);

  fAngle0Cmd = new G4UIcmdWithADoubleAndUnit("/polarimeter/geometry/AngleRing0", this);
  fAngle0Cmd->SetGuidance("Set scattering angle for ring 0.");
  fAngle0Cmd->SetParameterName("Angle0", false);
  fAngle0Cmd->SetDefaultUnit("deg");
  fAngle0Cmd->SetUnitCategory("Angle");
  fAngle0Cmd->AvailableForStates(G4State_PreInit);

  fAngle1Cmd = new G4UIcmdWithADoubleAndUnit("/polarimeter/geometry/AngleRing1", this);
  fAngle1Cmd->SetGuidance("Set scattering angle for ring 1.");
  fAngle1Cmd->SetParameterName("Angle1", false);
  fAngle1Cmd->SetDefaultUnit("deg");
  fAngle1Cmd->SetUnitCategory("Angle");
  fAngle1Cmd->AvailableForStates(G4State_PreInit);

  fNDetCmd = new G4UIcmdWithAnInteger("/polarimeter/geometry/NDetPerRing", this);
  fNDetCmd->SetGuidance("Set number of detectors per ring.");
  fNDetCmd->SetParameterName("NDet", false);
  fNDetCmd->AvailableForStates(G4State_PreInit);

  fUseDipoleCmd = new G4UIcmdWithABool("/polarimeter/geometry/UseDipole", this);
  fUseDipoleCmd->SetGuidance("Include SAMURAI dipole magnet.");
  fUseDipoleCmd->SetParameterName("UseDipole", false);
  fUseDipoleCmd->AvailableForStates(G4State_PreInit);

  fUseNEBULACmd = new G4UIcmdWithABool("/polarimeter/geometry/UseNEBULA", this);
  fUseNEBULACmd->SetGuidance("Include NEBULA neutron array.");
  fUseNEBULACmd->SetParameterName("UseNEBULA", false);
  fUseNEBULACmd->AvailableForStates(G4State_PreInit);
}

PolarimeterDetectorConstructionMessenger::~PolarimeterDetectorConstructionMessenger()
{
  delete fDistanceCmd;
  delete fAngle0Cmd;
  delete fAngle1Cmd;
  delete fNDetCmd;
  delete fUseDipoleCmd;
  delete fUseNEBULACmd;
  delete fDir;
}

void PolarimeterDetectorConstructionMessenger::SetNewValue(
    G4UIcommand* command, G4String newValue)
{
  if (command == fDistanceCmd) {
    fDetector->SetTargetDistance(fDistanceCmd->GetNewDoubleValue(newValue));
  } else if (command == fAngle0Cmd) {
    fDetector->SetAngleRing0(fAngle0Cmd->GetNewDoubleValue(newValue));
  } else if (command == fAngle1Cmd) {
    fDetector->SetAngleRing1(fAngle1Cmd->GetNewDoubleValue(newValue));
  } else if (command == fNDetCmd) {
    fDetector->SetNDetPerRing(fNDetCmd->GetNewIntValue(newValue));
  } else if (command == fUseDipoleCmd) {
    fDetector->SetUseDipole(fUseDipoleCmd->GetNewBoolValue(newValue));
  } else if (command == fUseNEBULACmd) {
    fDetector->SetUseNEBULA(fUseNEBULACmd->GetNewBoolValue(newValue));
  }
}
