#include "DET01PrimaryGeneratorAction.hh"

#include "G4Event.hh"
#include "G4ParticleGun.hh"
#include "G4ParticleTable.hh"
#include "G4ParticleDefinition.hh"
#include "G4SystemOfUnits.hh"
#include "Randomize.hh"
#include <cmath>

DET01PrimaryGeneratorAction::DET01PrimaryGeneratorAction()
 : G4VUserPrimaryGeneratorAction(),
   fParticleGun(0),
   fPy(0.7),     // Default hardcoded vector polarisation
   fTzz(0.5),    // Default hardcoded tensor polarisation
   fAy(0.4),     // Example analysing power
   fAzz(0.3),    // Example tensor analysing power
   fAxx_yy(0.1), // Example off-diagonal power
   fTxx_yy(0.0)  // Assume Txx = Tyy for simple testing
{
  G4int n_particle = 1;
  fParticleGun = new G4ParticleGun(n_particle);

  // Default particle kinematic
  G4ParticleTable* particleTable = G4ParticleTable::GetParticleTable();
  G4String particleName;
  G4ParticleDefinition* particle = particleTable->FindParticle(particleName="deuteron");
  fParticleGun->SetParticleDefinition(particle);
  
  // Energy: 190 MeV/u * 2 nucleons = 380 MeV
  fParticleGun->SetParticleEnergy(380.0*MeV);
}

DET01PrimaryGeneratorAction::~DET01PrimaryGeneratorAction()
{
  delete fParticleGun;
}

void DET01PrimaryGeneratorAction::GeneratePrimaries(G4Event* anEvent)
{
  // 1. Randomise Vertex Position within the CH2 target
  // Target dimensions: 5cm x 5cm x 1cm
  G4double x0 = (G4UniformRand() - 0.5) * 5.0 * cm;
  G4double y0 = (G4UniformRand() - 0.5) * 5.0 * cm;
  G4double z0 = (G4UniformRand() - 0.5) * 1.0 * cm;
  fParticleGun->SetParticlePosition(G4ThreeVector(x0, y0, z0));

  // 2. Rejection Sampling for Azimuthal Angle (phi)
  G4double phi = 0.0;
  G4bool accepted = false;
  
  // The maximum possible value of f(phi) occurs when cos(phi) and cos(2phi) terms align.
  // A safe upper bound is the sum of the absolute values of the coefficients.
  G4double f_max = 1.0 + std::abs(1.5 * fPy * fAy) + std::abs(0.5 * fTzz * fAzz) + std::abs(0.25 * fTxx_yy * fAxx_yy);

  while (!accepted) {
      phi = G4UniformRand() * 2.0 * M_PI;
      
      // Calculate probability density for this phi
      G4double f_phi = 1.0 
                       + 1.5 * fPy * fAy * std::cos(phi) 
                       + 0.5 * fTzz * fAzz 
                       + 0.25 * fTxx_yy * fAxx_yy * std::cos(2.0 * phi);
      
      // Safety check to prevent negative probabilities if unphysical parameters are given
      if (f_phi < 0.0) f_phi = 0.0;

      // Acceptance criterion
      G4double u = G4UniformRand() * f_max;
      if (u < f_phi) {
          accepted = true;
      }
  }

  // 3. Set Momentum Direction
  // Theta is fixed at 30 degrees to target the detector ring.
  G4double theta = 30.0 * deg;
  
  G4double px = std::sin(theta) * std::cos(phi);
  G4double py = std::sin(theta) * std::sin(phi);
  G4double pz = std::cos(theta);
  
  fParticleGun->SetParticleMomentumDirection(G4ThreeVector(px, py, pz));

  // Fire!
  fParticleGun->GeneratePrimaryVertex(anEvent);
}
