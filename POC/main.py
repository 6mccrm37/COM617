from Py6S import *
import matplotlib.pyplot as plt
from datetime import datetime

# Define the path to your compiled sixs executable
sixs_exe_path = r"C:\users\Martin\source\build\6SV\1.1\6SV1.1\sixsV1.1"

# Initialize SixS
s = SixS(sixs_exe_path)

# Set ground reflectance to Green Vegetation
s.ground_reflectance = GroundReflectance.HomogeneousLambertian(GroundReflectance.GreenVegetation)

# Set atmospheric profile using latitude & date
s.atmos_profile = AtmosProfile.FromLatitudeAndDate(50, "2024-07-14")

# Run the model
s.run()

#Print the generated input file for debugging
print("\n=== SixS Input File ===")
with open(s.write_input_file()) as f:
    print(f.read())

#Print full output text
print("\n=== SixS Full Output ===")
print(s.outputs.fulltext)

# ✅ Print key outputs
print("\n=== Key Outputs ===")
print(f"Apparent Reflectance: {s.outputs.apparent_reflectance}")
print(f"Apparent Radiance: {s.outputs.apparent_radiance}")
print(f"Water Vapor Transmittance (Downward): {s.outputs.transmittance_water.downward}")

#Run Landsat ETM simulation correctly
wavelengths, outputs = SixSHelpers.Wavelengths.run_landsat_etm(s, output_name='apparent_radiance')

#Plot the Landsat ETM spectral output
plt.figure(figsize=(8, 5))
plt.plot(wavelengths, outputs, label="Landsat ETM")
plt.xlabel("Wavelength (μm)")
plt.ylabel("Radiance (W/m²/sr/μm)")
plt.grid()
plt.legend()
plt.show()

#Test different AOT values
s.aot550 = 0.1
wavelengths, outputs_01 = SixSHelpers.Wavelengths.run_vnir(s, output_name="apparent_radiance")

s.aot550 = 2
wavelengths, outputs_2 = SixSHelpers.Wavelengths.run_vnir(s, output_name="apparent_radiance")

#Plot AOT variations
plt.figure(figsize=(8, 5))
plt.plot(wavelengths, outputs_01, label="AOT = 0.1")
plt.plot(wavelengths, outputs_2, label="AOT = 2.0")
plt.xlabel("Wavelength (μm)")
plt.ylabel("Radiance (W/m²/sr/μm)")
plt.grid()
plt.legend()
plt.show()
