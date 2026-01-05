#include "DET01ActionInitialization.hh"
#include "DET01PrimaryGeneratorAction.hh"
#include "DET01RunAction.hh"

DET01ActionInitialization::DET01ActionInitialization()
 : G4VUserActionInitialization()
{}

DET01ActionInitialization::~DET01ActionInitialization()
{}

void DET01ActionInitialization::BuildForMaster() const
{
  SetUserAction(new DET01RunAction());
}

void DET01ActionInitialization::Build() const
{
  SetUserAction(new DET01PrimaryGeneratorAction());
  SetUserAction(new DET01RunAction());
}
