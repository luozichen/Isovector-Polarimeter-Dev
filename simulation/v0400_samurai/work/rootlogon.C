{
  // ROOT logon for sim_polarimeter analysis.
  // Legacy smsimulator builds may leave libsmdata and its PCM in
  // smg4lib/data/sources instead of installing libsmg4data/libsmg4construction.
  // Load the actual smdata dictionary path first to avoid noisy missing-library
  // messages during quick ROOT file checks.

  const char* smsimEnv = gSystem->Getenv("SMSIMDIR");
  TString smsimdir = smsimEnv ? smsimEnv : "";
  if (smsimdir.IsNull()) {
    smsimdir = "/data4/luozc25/files/smsimulator5.5";
  }

  const char* tartEnv = gSystem->Getenv("TARTSYS");
  TString tartsys = tartEnv ? tartEnv : "";
  if (!tartsys.IsNull()) {
    gSystem->AddDynamicPath(Form("%s/lib", tartsys.Data()));
  }

  TString smg4lib = smsimdir + "/smg4lib";
  TString smdataBuildDir = smg4lib + "/data/sources";
  TString smdataLibDir = smdataBuildDir + "/.libs";

  gSystem->AddDynamicPath(smdataBuildDir);
  gSystem->AddDynamicPath(smdataLibDir);
  gSystem->AddDynamicPath(smg4lib + "/lib");
  gInterpreter->AddIncludePath(smdataBuildDir + "/include");

  Int_t smdataStatus = -1;
  TString smdataSo = smdataLibDir + "/libsmdata.so";
  if (!gSystem->AccessPathName(smdataSo)) {
    smdataStatus = gSystem->Load(smdataSo);
  } else {
    smdataStatus = gSystem->Load("libsmdata");
  }

  if (smdataStatus < 0) {
    std::cerr << "Warning: failed to load smdata dictionary library." << std::endl;
    std::cerr << "         Expected either " << smdataSo << " or libsmdata in the dynamic path." << std::endl;
  }

  gStyle->SetOptStat(1111);
  gStyle->SetOptFit(1);
  gStyle->SetPalette(kBird);

  std::cout << "=== sim_polarimeter ROOT session ===" << std::endl;
  std::cout << "  SMSIMDIR=" << smsimdir << std::endl;
  std::cout << "  smdata load status=" << smdataStatus << std::endl;
}
