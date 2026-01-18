#ifndef DET01EventAction_h
#define DET01EventAction_h 1

#include "G4UserEventAction.hh"
#include "globals.hh"

class DET01EventAction : public G4UserEventAction
{
  public:
    DET01EventAction();
    virtual ~DET01EventAction();

    virtual void BeginOfEventAction(const G4Event* event);
    virtual void EndOfEventAction(const G4Event* event);

  private:
    G4int fScintHCID;
    G4int fPmtHCID;
};

#endif
