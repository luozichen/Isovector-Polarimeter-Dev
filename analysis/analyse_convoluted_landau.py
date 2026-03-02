import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import moyal
import scipy.integrate as integrate

# Parameters (in mm) based on G4 simulation (v0200_coincidence)
# G4 dimensions: Scintillator = 120 x 150 x 150 mm, Gap = 8.5 mm
size_x = 120.0
size_y = 150.0
size_z = 150.0
gap = 8.5

# Detector geometry
# As per the user's derivation: H is the distance from the bottom face of the top det
# to the top face of the bottom det.
# H = gap + size_z + gap + size_z + gap = 2 * size_z + 3 * gap
H = 2 * size_z + 3 * gap  # Total height between limiting planes
L0_mm = size_z            # Vertical path length in a single detector (mm)
L0_cm = L0_mm / 10.0      # in cm (15.0 cm)

# Acceptance function
def acceptance(theta, phi):
    dx = H * np.tan(theta) * np.abs(np.cos(phi))
    dy = H * np.tan(theta) * np.abs(np.sin(phi))
    
    overlap_x = np.maximum(0, size_x - dx)
    overlap_y = np.maximum(0, size_y - dy)
    return overlap_x * overlap_y

# Weight function for theta (integrating over phi)
def weight_theta(theta):
    # Integrate over phi (0 to pi/2, then multiply by 4 for symmetry)
    phi_vals = np.linspace(0, np.pi/2, 100)
    A_vals = acceptance(theta, phi_vals)
    integral_phi = np.trapz(A_vals, phi_vals) * 4
    
    # Weight includes cosmic ray flux (cos^2(theta)) and solid angle (sin(theta))
    # AND the horizontal surface projection factor (cos(theta)). Total: cos^3(theta) * sin(theta)
    return np.cos(theta)**3 * np.sin(theta) * integral_phi

# Max theta
tan_theta_max = np.sqrt(size_x**2 + size_y**2) / H
theta_max = np.arctan(tan_theta_max)

# Create theta array
theta_vals = np.linspace(0, theta_max, 200)
W_vals = np.array([weight_theta(th) for th in theta_vals])

# Normalize weights
W_norm = W_vals / np.trapz(W_vals, theta_vals)

# Energy array (MeV)
E_vals = np.linspace(15, 60, 500)

# 1. Vertical Landau (Approximated using Moyal)
# MPV = 30 MeV, xi = 3 MeV
dist_vertical = moyal.pdf(E_vals, loc=30.0, scale=3.0)

# 2. Convoluted Landau
dist_convoluted = np.zeros_like(E_vals)

for i, theta in enumerate(theta_vals):
    if W_norm[i] > 0:
        L_cm = L0_cm / np.cos(theta)
        # MPV reference is ~30 MeV for 15cm thickness (2.0 MeV/cm)
        # Scale reference is ~3 MeV for 15cm thickness (0.2 MeV/cm)
        mpv = L_cm * 2.0 
        scale = L_cm * 0.2
        
        pdf = moyal.pdf(E_vals, loc=mpv, scale=scale)
        dist_convoluted += W_norm[i] * pdf * (theta_vals[1] - theta_vals[0]) # d_theta approximation

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(E_vals, dist_vertical, label='Perfectly Vertical (Pure Moyal/Landau)', linestyle='--', color='blue', linewidth=2)
plt.plot(E_vals, dist_convoluted, label='Path-Convoluted (4-Fold Trigger)', color='red', linewidth=2)

plt.title('Energy Deposition Distribution in Inner Detector', fontsize=14)
plt.xlabel('Energy Deposited (MeV)', fontsize=12)
plt.ylabel('Probability Density', fontsize=12)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.5)
plt.tight_layout()
plt.savefig('results/simulation/landau_convolution.png')
plt.close()

print("Plot saved successfully to results/simulation/landau_convolution.png.")
