#include "DET01PrimaryGeneratorAction.hh"

#include "G4Event.hh"
#include "G4GeneralParticleSource.hh"
#include "G4ParticleTable.hh"
#include "G4ParticleDefinition.hh"
#include "G4SystemOfUnits.hh"

DET01PrimaryGeneratorAction::DET01PrimaryGeneratorAction()
 : G4VUserPrimaryGeneratorAction(),
   fParticleGun(0)
{
  fParticleGun = new G4GeneralParticleSource();
}

DET01PrimaryGeneratorAction::~DET01PrimaryGeneratorAction()
{
  delete fParticleGun;
}

void DET01PrimaryGeneratorAction::GeneratePrimaries(G4Event* anEvent)
{
  fParticleGun->GeneratePrimaryVertex(anEvent);
}
