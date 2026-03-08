#include "DET01PhysicsList.hh"

#include "QGSP_BIC_HP.hh"
#include "G4OpticalPhysics.hh"

DET01PhysicsList::DET01PhysicsList() : QGSP_BIC_HP()
{
  // 2. G4OpticalPhysics for scintillation and Cherenkov
  G4OpticalPhysics* opticalPhysics = new G4OpticalPhysics();
  RegisterPhysics(opticalPhysics);
}

DET01PhysicsList::~DET01PhysicsList()
{
}
