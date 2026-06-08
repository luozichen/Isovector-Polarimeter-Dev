# Geant4 Simulation: Cylindrical Scintillator Geometric Timing Jitter

This document explains the physical concepts of the simulated **geometric timing jitter** for the SP101 cylindrical scintillator coincidence setup ($\varnothing\,40$ mm diameter, $10$ mm thickness, $5.0$ mm air gap) and details how it is mathematically extracted from the high-statistics simulation ROOT file.

---

## 1. Physical Concepts

### 1.1 What is Geometric Propagation Jitter?
The **geometric timing jitter** ($\sigma_{\text{geom}}$) is the temporal dispersion of scintillation photons propagating from the interaction vertex (where the cosmic muon deposits energy) to the PMT photocathode. 
When a cosmic ray muon traverses the active volume of the plastic scintillator, it generates scintillation photons along its track. These photons propagate in all directions, undergoing multiple reflections at the boundaries. The first photon arrival time at the photocathode window defines the timing signal of the detector.
Because the interaction vertices are distributed throughout the active volume, and the photon paths can vary depending on the entry angle and position, the propagation path lengths fluctuate. This path length variation directly translates to a fluctuation in the arrival time of the first photons, which constitutes the geometric propagation jitter.

### 1.2 Why is the Cylindrical Jitter so Small?
* **Compact Dimensions:** The SP101 cylindrical scintillator is extremely thin ($10$ mm) and compact ($\varnothing\,40$ mm), meaning that the maximum possible photon path difference is only a few centimeters. In comparison, the cuboid scintillators are massive ($150 \times 150 \times 120$ mm), allowing for much longer photon travel paths and larger dispersion ($\sigma_{\text{geom}}^{\text{cuboid}} \approx 450$ ps).
* **Speed of Light in Scintillator:** The speed of light in the PVT (polyvinyltoluene) plastic medium is $v = c/n \approx 3 \times 10^8\text{ m/s} / 1.59 \approx 18.9\text{ cm/ns} \approx 19\text{ ps/mm}$. A path fluctuation of $\pm 1$ mm corresponds to a timing variation of only $\sim 19$ ps. For first-photon arrival timing under a coincidence constraint, the vertices are centered, reducing path fluctuations to a standard deviation of **$\sigma_{\text{geom}} \approx 3.5$ ps**.

### 1.3 Mean Offset vs. Timing Jitter
In the simulation, the average timing difference between the two PMTs is:
$$\langle \text{Time\_PMT0} - \text{Time\_PMT1} \rangle \approx -98\text{ ps}$$
This is the **muon transit time** plus the optical path asymmetry. The distance between the midpoints of the two scintillators is $15$ mm ($5$ mm half-thickness + $5$ mm air gap + $5$ mm half-thickness). For a relativistic cosmic muon traveling at $v \approx c \approx 300$ mm/ns, the travel time across $15$ mm is:
$$\Delta t_{\text{muon}} = \frac{15\text{ mm}}{300\text{ mm/ns}} = 0.050\text{ ns} = 50\text{ ps}$$
This $50$ ps transit time is a **constant offset** (mean shift) and does not contribute to the timing *jitter* (random fluctuations). The jitter is defined strictly by the **standard deviation** (width) of the timing distribution, which is $\sim 5$ ps. 

---

## 2. Extraction from ROOT File

The timing properties are extracted from the ROOT file `DET01_Cosmic_Result_long.root` containing $10,000,000$ simulated events.

### 2.1 Variables in ROOT Tree
* `Time_PMT0`: Arrival time of the first scintillation photon at the top PMT photocathode (in ns).
* `Time_PMT1`: Arrival time of the first scintillation photon at the bottom PMT photocathode (in ns).
* `PE_PMT0`: Photoelectron (PE) count in the top PMT.
* `PE_PMT1`: Photoelectron (PE) count in the bottom PMT.

### 2.2 Coincidence Logic and Math
To replicate the hardware trigger, we apply a double-coincidence cut requiring significant light deposition in both detectors:
$$\text{Cut: } \text{PE\_PMT0} > 50 \text{ and } \text{PE\_PMT1} > 50$$
This yields $16,286$ coincident events out of $10,000,000$ total events. We calculate the relative time difference:
$$\Delta t = \text{Time\_PMT0} - \text{Time\_PMT1}$$

The timing difference is binned into a histogram with $200$ bins in the range $[-0.1, 0.1]$ ns. We fit a Gaussian function:
$$f(\Delta t) = A \exp\left(-\frac{(\Delta t - \mu)^2}{2\sigma_{\text{pair}}^2}\right)$$

* **Pair Jitter ($\sigma_{\text{pair}}$):** Standard deviation of the relative timing difference.
* **Single Detector Jitter ($\sigma_{\text{single}}$):** Under the assumption of independent, identical detectors, the single detector geometric propagation jitter is:
$$\sigma_{\text{single}} = \frac{\sigma_{\text{pair}}}{\sqrt{2}}$$

### 2.3 Python Extraction Code
The following SciPy script is used to perform the fit on the raw ROOT data:
```python
import uproot
import numpy as np
from scipy.optimize import curve_fit

def gaussian(x, amp, mean, sigma):
    return amp * np.exp(-0.5 * ((x - mean) / sigma) ** 2)

# Load branches from ROOT tree
with uproot.open("DET01_Cosmic_Result_long.root") as file:
    df = file["CosmicData"].arrays(["Time_PMT0", "Time_PMT1", "PE_PMT0", "PE_PMT1"], library="pd")

# Apply coincidence cut
coinc_df = df[(df["PE_PMT0"] > 50) & (df["PE_PMT1"] > 50)]
dt = coinc_df["Time_PMT0"] - coinc_df["Time_PMT1"]

# Fit Gaussian
counts, bin_edges = np.histogram(dt, bins=200, range=(-0.1, 0.1))
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
popt, _ = curve_fit(gaussian, bin_centers, counts, p0=[np.max(counts), np.mean(dt), np.std(dt)])

sigma_pair = abs(popt[2])
sigma_single = sigma_pair / np.sqrt(2.0)

print(f"Fitted pair jitter: {sigma_pair * 1000:.3f} ps")
print(f"Single detector jitter: {sigma_single * 1000:.3f} ps")
```

### 2.4 Extraction Results
From the $10$M event run, the fit yields:
* **Raw Standard Deviation:** `5.023 ps`
* **Fitted Coincidence Pair Jitter ($\sigma_{\text{pair}}$):** **`4.300 ps` ($0.0043$ ns)**
* **Fitted Single Detector Jitter ($\sigma_{\text{single}}$):** **`3.041 ps` ($0.0030$ ns)**

This demonstrates that the geometric timing jitter is extremely small ($\sim 3\text{--}5$ ps), and that the physical timing resolution ($\sim 1\text{--}1.5$ ns) is dominated by the PMT transit time spread (TTS $\approx 1$ ns) and electronic chain fluctuations rather than the scintillator geometry.
