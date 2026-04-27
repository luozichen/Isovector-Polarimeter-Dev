// ============================================================
// sim_polarimeter.cc
// Main program for the SAMURAI polarimeter simulation
// Based on smsimulator5.5 framework (sim_samurai21 pattern)
// ============================================================

#include "G4RunManager.hh"
#include "G4UImanager.hh"
#include "G4UIterminal.hh"
#include "G4UItcsh.hh"
#include "G4UIExecutive.hh"
#include <iostream>
#include <vector>

#ifdef G4VIS_USE
#include "G4VisExecutive.hh"
#endif

// smg4lib/action
using std::ostream;
using std::istream;
#include "PrimaryGeneratorActionBasic.hh"
#include "EventActionBasic.hh"
#include "RunActionBasic.hh"
#include "TrackingActionBasic.hh"

// smg4lib/data
#include "SimDataManager.hh"
#include "FragSimDataConverter_Basic.hh"
#include "TBeamSimData.hh"

// smg4lib/physics
#include "QGSP_BIC_XS.hh"

// Local
#include "PolarimeterDetectorConstruction.hh"

// ROOT
#include "TROOT.h"
#include "TApplication.h"
#include "TSystem.h"

int main(int argc, char** argv)
{
  // Preserve the Geant4 macro argument before ROOT may rewrite argc/argv.
  const bool hasMacroArg = (argc > 1);
  G4String macroFile;
  if (hasMacroArg) macroFile = argv[1];

  // ROOT application (needed for TFile output)
  TApplication app("app", &argc, argv);

  // Construct the run manager
  G4RunManager* runManager = new G4RunManager;

  // === Detector Construction ===
  PolarimeterDetectorConstruction* detector = new PolarimeterDetectorConstruction;
  runManager->SetUserInitialization(detector);

  // === Physics List ===
  // QGSP_BIC_XS: standard for intermediate-energy nuclear reactions
  // Includes Geant4 binary cascade for p, n, d, t, 3He, alpha
  // with additional cross-section data
  G4VUserPhysicsList* physics = new QGSP_BIC_XS;
  runManager->SetUserInitialization(physics);

  // === User Actions ===
  // PrimaryGeneratorActionBasic: configurable via /action/gun/ commands
  runManager->SetUserAction(new PrimaryGeneratorActionBasic);
  runManager->SetUserAction(new RunActionBasic);
  runManager->SetUserAction(new EventActionBasic);
  runManager->SetUserAction(new TrackingActionBasic);

  // === SimData Converters ===
  // FragSimDataConverter_Basic can crash on legacy setups when
  // FragSimDataArray is not initialized by the framework.
  SimDataManager* simDataManager = SimDataManager::GetSimDataManager();
  // simDataManager->RegistConverter(new FragSimDataConverter_Basic);
  // Legacy smg4lib builds may not initialize beam storage automatically,
  // which can leave gBeamSimDataArray null in Pencil generation mode.
  if (!gBeamSimDataArray) {
    gBeamSimDataArray = new std::vector<TBeamSimData>;
  }

#ifdef G4VIS_USE
  // Visualization is only needed for interactive sessions.
  G4VisManager* visManager = nullptr;
  if (!hasMacroArg) {
    visManager = new G4VisExecutive;
    visManager->Initialize();
  }
#endif

  // Get the pointer to the UI manager
  G4UImanager* UImanager = G4UImanager::GetUIpointer();

  if (hasMacroArg) {
    // Batch mode: execute macro file
    G4String command = "/control/execute ";
    UImanager->ApplyCommand(command + macroFile);
  } else {
    // Interactive mode: Detects Qt automatically
    G4UIExecutive* ui = new G4UIExecutive(argc, argv);
 
    ui->SessionStart();
    delete ui;
  }

  // Cleanup
#ifdef G4VIS_USE
  delete visManager;
#endif
  delete runManager;

  return 0;
}
