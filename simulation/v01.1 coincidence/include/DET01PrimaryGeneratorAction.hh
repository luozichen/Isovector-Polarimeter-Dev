#ifndef DET01PrimaryGeneratorAction_h
#define DET01PrimaryGeneratorAction_h 1

#include "G4VUserPrimaryGeneratorAction.hh"
#include "G4GeneralParticleSource.hh"
#include "globals.hh"

class G4Event;

class DET01PrimaryGeneratorAction : public G4VUserPrimaryGeneratorAction
{
  public:
    DET01PrimaryGeneratorAction();
    virtual ~DET01PrimaryGeneratorAction();

    virtual void GeneratePrimaries(G4Event*);

    const G4GeneralParticleSource* GetParticleGun() const { return fParticleGun; }

  private:
    G4GeneralParticleSource*  fParticleGun;
};

#endif
