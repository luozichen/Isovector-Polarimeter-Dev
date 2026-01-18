#include "G4RunManagerFactory.hh"
#include "G4UImanager.hh"
#include "G4VisExecutive.hh"
#include "G4UIExecutive.hh"

#include "DET01DetectorConstruction.hh"
#include "DET01PhysicsList.hh"
#include "DET01ActionInitialization.hh"

int main(int argc, char** argv)
{
  // Construct the default run manager
  auto* runManager = G4RunManagerFactory::CreateRunManager(G4RunManagerType::Default);

  // Set mandatory initialization classes
  runManager->SetUserInitialization(new DET01DetectorConstruction());
  runManager->SetUserInitialization(new DET01PhysicsList());
  runManager->SetUserInitialization(new DET01ActionInitialization());

  // Initialize visualization
  G4VisManager* visManager = new G4VisExecutive;
  visManager->Initialize();

  // Get the pointer to the User Interface manager
  G4UImanager* UImanager = G4UImanager::GetUIpointer();

  if (argc != 1) {
    // batch mode
    G4String command = "/control/execute ";
    G4String fileName = argv[1];
    UImanager->ApplyCommand(command + fileName);
  }
  else {
    // interactive mode
    G4UIExecutive* ui = new G4UIExecutive(argc, argv);
    UImanager->ApplyCommand("/control/execute init_vis.mac"); // We will need this file
    ui->SessionStart();
    delete ui;
  }

  // Job termination
  delete visManager;
  delete runManager;
  return 0;
}
