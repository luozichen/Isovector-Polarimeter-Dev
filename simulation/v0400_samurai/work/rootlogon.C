{
  // ROOT logon for sim_polarimeter analysis
  // Load smg4lib data library for TSimData etc.

  gSystem->Load("libsmg4data");
  gSystem->Load("libsmg4construction");

  gStyle->SetOptStat(1111);
  gStyle->SetOptFit(1);
  gStyle->SetPalette(kBird);

  std::cout << "=== sim_polarimeter ROOT session ===" << std::endl;
  std::cout << "  smg4data and smg4construction libraries loaded." << std::endl;
}
