# ============================================================
# GNUmakefile for sim_polarimeter
# Follows smsimulator5.5 build conventions
# ============================================================

name := sim_polarimeter

G4TARGET := $(name)
G4EXLIB := true

CPPFLAGS += -I$(SMSIMULATOR)/smg4lib/action/include
CPPFLAGS += -I$(SMSIMULATOR)/smg4lib/construction/include
CPPFLAGS += -I$(SMSIMULATOR)/smg4lib/data/sources/include
CPPFLAGS += -I$(SMSIMULATOR)/smg4lib/physics/include

EXTRALIBS += -L$(SMSIMULATOR)/smg4lib/action/lib      -lsmg4action
EXTRALIBS += -L$(SMSIMULATOR)/smg4lib/construction/lib -lsmg4construction
EXTRALIBS += -L$(SMSIMULATOR)/smg4lib/physics/lib      -lsmg4physics

EXTRALIBS += -L$(SMSIMULATOR)/smg4lib/data/sources -lsmg4data

CPPFLAGS += $(shell root-config --cflags)
EXTRALIBS += $(shell root-config --libs)

ifndef G4INSTALL
  G4INSTALL = ../../..
endif

.PHONY: all
all: lib bin

include $(G4INSTALL)/config/binmake.gmk
