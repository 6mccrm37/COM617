import matplotlib.pyplot as plt
from Py6S import SixS, SixSHelpers

# Define the path to your 6S executable
sixs_exe_path = r"C:\users\Martin\source\build\6SV\1.1\6SV1.1\sixsV1.1"

# Initialize SixS
s = SixS(sixs_exe_path)

# Run the VNIR (Visible and Near Infrared) simulation
wavelengths, results = SixSHelpers.Wavelengths.run_vnir(s, output_name="pixel_radiance")

# Plot the results using matplotlib
plt.figure(figsize=(8, 5))
plt.plot(wavelengths, results, marker="o", linestyle="-", label="Pixel Radiance")
plt.xlabel("Wavelength (μm)")
plt.ylabel("Radiance")
plt.title("VNIR Pixel Radiance Spectrum")
plt.legend()
plt.grid(True)
plt.show()




