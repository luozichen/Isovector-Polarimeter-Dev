# Mathematical Derivation of $R_{LRUD}$ and Spin-1 Cartesian Cross-Section Coefficients

This document provides a detailed mathematical derivation of the polarized cross-section and the Left-Right-Up-Down sum asymmetry ($R_{LRUD}$) for deuteron-proton ($d$-$p$) elastic scattering. It resolves the coefficient inconsistencies found between the initial thesis drafting, *Paper 3* (arXiv:2506.15738v2), and standard nuclear polarimetry literature.

---

## 1. Definitions and Notation Conventions

### 1.1 Projectile Helicity Frame (Madison Convention)
Following the standard **Madison convention**, we define the right-handed Cartesian coordinate system $(x, y, z)$ as follows:
* **$z$-axis**: Aligned with the direction of the incident beam momentum ($\hat{z} = \hat{k}_{\text{in}}$).
* **$y$-axis**: Normal to the reaction plane, defined by the cross product of the incident and outgoing momenta:
  $$\hat{y} = \frac{\vec{k}_{\text{in}} \times \vec{k}_{\text{out}}}{|\vec{k}_{\text{in}} \times \vec{k}_{\text{out}}|}$$
* **$x$-axis**: Lies in the reaction plane, completing the right-handed frame:
  $$\hat{x} = \hat{y} \times \hat{z}$$

### 1.2 Spin-1 Polarisation Observables
The polarization state of a spin-1 deuteron beam in the Cartesian representation is defined by:
1. **Vector polarization components (rank-1)**:
   $$p_i = \langle S_i \rangle, \quad i \in \{x, y, z\}$$
2. **Tensor polarization components (rank-2, symmetric and traceless)**:
   $$p_{ij} = \langle P_{ij} \rangle = \langle 3 S_i S_j - 2 \delta_{ij} \rangle, \quad i,j \in \{x,y,z\}$$
   By the traceless condition, the diagonal components satisfy:
   $$p_{xx} + p_{yy} + p_{zz} = 0$$

### 1.3 Theoretical Tensor Moments ($T_{ij}$)
In some theoretical literature (and the main body of this thesis), the spin-1 tensor operators are defined as:
$$T_{ij} = \frac{1}{2} \langle S_i S_j + S_j S_i \rangle - \frac{2}{3} \delta_{ij}$$
Comparing this theoretical definition with the experimental Madison convention observables $p_{ij}$, we obtain the mapping:
$$p_{ij} = 3 T_{ij} \implies T_{ij} = \frac{1}{3} p_{ij}$$

---

## 2. Polarised Differential Cross Section

Under the Madison convention, the differential cross section $\sigma(\theta, \phi)$ for a polarized spin-1 beam incident on an unpolarized target is expressed as:
$$\sigma(\theta, \phi) = \sigma_0(\theta) \left[ 1 + \frac{3}{2} p_y A_y(\theta) \cos \phi + \frac{1}{2} p_{zz} A_{zz}(\theta) + \frac{1}{6} (p_{xx} - p_{yy}) (A_{xx}(\theta) - A_{yy}(\theta)) \cos 2\phi \right]$$
where:
* $\sigma_0(\theta)$ is the unpolarized cross section.
* $A_y(\theta)$ is the vector analyzing power.
* $A_{xx}, A_{yy}, A_{zz}$ are the Cartesian tensor analyzing powers (satisfying $A_{xx} + A_{yy} + A_{zz} = 0$).
* $\phi$ is the azimuthal angle relative to the $x$-axis.

### 2.1 Mapping to Theoretical Moments ($T_{ij}$)
To express the cross section in terms of the theoretical moments $T_{ij}$, we substitute $p_{ij} = 3 T_{ij}$ and define $A_{xx-yy} \equiv A_{xx} - A_{yy}$:
$$\sigma(\theta, \phi) = \sigma_0 \left[ 1 + \frac{3}{2} P_y A_y \cos \phi + \frac{1}{2} (3 T_{zz}) A_{zz} + \frac{1}{6} \left( 3 T_{xx} - 3 T_{yy} \right) A_{xx-yy} \cos 2\phi \right]$$
Simplifying the coefficients yields the **mathematically correct cross-section formula**:
$$\sigma(\theta, \phi) = \sigma_0 \left[ 1 + \frac{3}{2} P_y A_y \cos \phi + \frac{3}{2} T_{zz} A_{zz} + \frac{1}{2} (T_{xx} - T_{yy}) A_{xx-yy} \cos 2\phi \right]$$

> [!WARNING]
> **Typo in the Thesis**: Equation (eq:cross_section) in the draft mistakenly wrote the coefficients of $T_{zz} A_{zz}$ and $(T_{xx} - T_{yy}) A_{xx-yy}$ as $\frac{1}{2}$ and $\frac{1}{4}$ respectively. This mixed up the theoretical $T_{ij}$ and experimental $p_{ij}$ coefficients.

---

## 3. Derivation of the $R_{LRUD}$ Asymmetry

We now derive the Left-Right-Up-Down asymmetry ratio $R_{LRUD}$ under **transverse axial symmetry**.

### 3.1 Beam Physical Symmetry Conditions
For a deuteron beam prepared in a pure transverse tensor-polarized state aligned along the $y$-axis (vertical transverse axis), the polarization tensor must exhibit axial symmetry about this axis. This physically dictates:
$$p_{xx} = p_{zz}$$
Using the traceless condition $p_{xx} + p_{yy} + p_{zz} = 0$, we find:
$$p_{zz} = -\frac{1}{2} p_{yy} \quad \text{and} \quad p_{xx} = -\frac{1}{2} p_{yy}$$
The difference between the transverse components becomes:
$$p_{xx} - p_{yy} = -\frac{1}{2} p_{yy} - p_{yy} = -\frac{3}{2} p_{yy}$$

### 3.2 Evaluating the Azimuthal Cross Section
Plugging these axial symmetry constraints into the standard Madison cross-section formula:
$$\sigma(\theta, \phi) = \sigma_0 \left[ 1 + \frac{3}{2} p_y A_y \cos \phi + \frac{1}{2} \left(-\frac{1}{2} p_{yy}\right) A_{zz} + \frac{1}{6} \left(-\frac{3}{2} p_{yy}\right) (A_{xx} - A_{yy}) \cos 2\phi \right]$$
$$\sigma(\theta, \phi) = \sigma_0 \left[ 1 + \frac{3}{2} p_y A_y \cos \phi - \frac{1}{4} p_{yy} A_{zz} - \frac{1}{4} p_{yy} (A_{xx} - A_{yy}) \cos 2\phi \right]$$

### 3.3 Event Yields in the Four Sectors
The event counts in the Left ($L$), Right ($R$), Up ($U$), and Down ($D$) detectors are proportional to the cross section evaluated at $\phi = 0, \pi, \pi/2, 3\pi/2$, respectively:
* **Left ($\phi = 0$, $\cos \phi = 1$, $\cos 2\phi = 1$):**
  $$N_L = N_0 \left[ 1 + \frac{3}{2} p_y A_y - \frac{1}{4} p_{yy} A_{zz} - \frac{1}{4} p_{yy} (A_{xx} - A_{yy}) \right]$$
* **Right ($\phi = \pi$, $\cos \phi = -1$, $\cos 2\phi = 1$):**
  $$N_R = N_0 \left[ 1 - \frac{3}{2} p_y A_y - \frac{1}{4} p_{yy} A_{zz} - \frac{1}{4} p_{yy} (A_{xx} - A_{yy}) \right]$$
* **Up ($\phi = \pi/2$, $\cos \phi = 0$, $\cos 2\phi = -1$):**
  $$N_U = N_0 \left[ 1 - \frac{1}{4} p_{yy} A_{zz} + \frac{1}{4} p_{yy} (A_{xx} - A_{yy}) \right]$$
* **Down ($\phi = 3\pi/2$, $\cos \phi = 0$, $\cos 2\phi = -1$):**
  $$N_D = N_0 \left[ 1 - \frac{1}{4} p_{yy} A_{zz} + \frac{1}{4} p_{yy} (A_{xx} - A_{yy}) \right]$$

### 3.4 Calculating the Asymmetry Ratio
The $R_{LRUD}$ ratio is defined as:
$$R_{LRUD} = \frac{N_L + N_R - N_U - N_D}{N_L + N_R + N_U + N_D}$$

1. **Numerator**:
   $$N_L + N_R = 2 N_0 \left[ 1 - \frac{1}{4} p_{yy} A_{zz} - \frac{1}{4} p_{yy} (A_{xx} - A_{yy}) \right]$$
   $$N_U + N_D = 2 N_0 \left[ 1 - \frac{1}{4} p_{yy} A_{zz} + \frac{1}{4} p_{yy} (A_{xx} - A_{yy}) \right]$$
   Subtracting them:
   $$(N_L + N_R) - (N_U + N_D) = -p_{yy} N_0 (A_{xx} - A_{yy})$$
   *(Note: The vector polarization term $p_y A_y$ cancels out completely in the addition $N_L + N_R$, isolating the tensor terms.)*

2. **Denominator**:
   $$(N_L + N_R) + (N_U + N_D) = 2 N_0 \left[ 2 \left( 1 - \frac{1}{4} p_{yy} A_{zz} \right) \right] = N_0 (4 - p_{yy} A_{zz})$$

3. **Final Ratio**:
   $$R_{LRUD} = \frac{-N_0 p_{yy} (A_{xx} - A_{yy})}{N_0 (4 - p_{yy} A_{zz})} = \frac{p_{yy} (A_{xx} - A_{yy})}{p_{yy} A_{zz} - 4}$$

This mathematically confirms **Equation (448)** of the thesis is 100% correct.

---

## 4. Resolving Discrepancies

### 4.1 Inconsistency in Paper 3 (arXiv:2506.15738v2, Equation 10)
Equation (10) in Paper 3 is written as:
$$R_{LRUD} = \frac{p_{y'y'} (A_{xx} - A_{yy})}{2 p_{y'y'} A_{zz} - 4}$$
This denominator differs by a factor of 2. 
* **Root Cause**: The authors of Paper 3 assumed $p_{z'z'} = -p_{y'y'}$ in the denominator.
* **Why it is incorrect**: If $p_{z'z'} = -p_{y'y'}$, then $p_{x'x'} = 0$ is required by the trace-zero condition. However, having $p_{x'x'} = 0$ while $p_{z'z'} \neq 0$ violates the transverse axial symmetry ($p_{x'x'} = p_{z'z'}$) required for a beam polarized along $y'$. 
* Furthermore, if $p_{x'x'} = 0$ were true, the numerator would gain an extra factor of $\frac{2}{3}$ which is missing in Paper 3's Equation (10). Thus, Paper 3 is internally inconsistent, and the thesis's formula (Eq. 448) is the correct one.

### 4.2 Required Corrections in Chapter 2
To make the thesis internally consistent, the intermediate formulas in Section 2.6 must be updated:
1. **Cross-Section Equation**:
   * *Old*: $\frac{1}{\sigma_0}\,\frac{\mathrm{d}\sigma}{\mathrm{d}\Omega}(\theta,\phi) = 1 + \frac{3}{2}\,P_y\,A_y\,\cos\phi + \frac{1}{2}\,T_{zz}\,A_{zz} + \frac{1}{4}\,(T_{xx} - T_{yy})\,A_{xx-yy}\,\cos 2\phi$
   * *New*: $\frac{1}{\sigma_0}\,\frac{\mathrm{d}\sigma}{\mathrm{d}\Omega}(\theta,\phi) = 1 + \frac{3}{2}\,P_y\,A_y\,\cos\phi + \mathbf{\frac{3}{2}}\,T_{zz}\,A_{zz} + \mathbf{\frac{1}{2}}\,(T_{xx} - T_{yy})\,A_{xx-yy}\,\cos 2\phi$
2. **Left-Right Asymmetry ($\epsilon_{LR}$)**:
   * *Old*: $\epsilon_{LR} = \frac{3 P_y A_y}{2 + T_{zz} A_{zz}}$
   * *New*: $\epsilon_{LR} = \frac{3 P_y A_y}{2 + \mathbf{3} T_{zz} A_{zz}}$
3. **Up-Down Asymmetry ($\epsilon_{UD}$)**:
   * *Old*: $\epsilon_{UD} = \frac{3 P_x A_y}{2 + T_{zz} A_{zz}}$
   * *New*: $\epsilon_{UD} = \frac{3 P_x A_y}{2 + \mathbf{3} T_{zz} A_{zz}}$
4. **Transverse Asymmetry ($\epsilon_{T}$)**:
   * *Old*: $\epsilon_{T} = \frac{\frac{1}{2}(T_{xx} - T_{yy}) A_{xx-yy}}{2 + T_{zz} A_{zz}}$
   * *New*: $\epsilon_{T} = \frac{\mathbf{(T_{xx} - T_{yy})} A_{xx-yy}}{2 + \mathbf{3} T_{zz} A_{zz}}$
