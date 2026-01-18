#ifndef DET01RunAction_h
#define DET01RunAction_h 1

#include "G4UserRunAction.hh"
#include "G4AnalysisManager.hh"
#include "globals.hh"

class G4Run;

class DET01RunAction : public G4UserRunAction
{
  public:
    DET01RunAction();
    virtual ~DET01RunAction();

    virtual void BeginOfRunAction(const G4Run*);
    virtual void   EndOfRunAction(const G4Run*);
};

#endif
