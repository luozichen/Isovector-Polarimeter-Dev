#ifndef DET01PrimaryGeneratorAction_h
#define DET01PrimaryGeneratorAction_h 1

#include "G4VUserPrimaryGeneratorAction.hh"
#include "G4ParticleGun.hh"
#include "globals.hh"

class G4Event;

class DET01PrimaryGeneratorAction : public G4VUserPrimaryGeneratorAction
{
  public:
    DET01PrimaryGeneratorAction();
    virtual ~DET01PrimaryGeneratorAction();

    virtual void GeneratePrimaries(G4Event*);

    const G4ParticleGun* GetParticleGun() const { return fParticleGun; }

    // Setters for polarisation parameters
    void SetPy(G4double val) { fPy = val; }
    void SetTzz(G4double val) { fTzz = val; }
    void SetAy(G4double val) { fAy = val; }
    void SetAzz(G4double val) { fAzz = val; }

  private:
    G4ParticleGun* fParticleGun;

    // Physics parameters
    G4double fPy;
    G4double fTzz;
    G4double fAy;
    G4double fAzz;
    
    // Derived analyzing powers (simplified for testing)
    G4double fAxx_yy;
    G4double fTxx_yy;
};

#endif
