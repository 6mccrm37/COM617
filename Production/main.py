from Py6S import *
import matplotlib.pyplot as plt
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)

# Define the path to the sixs executable
sixs_exe_path = Path(r"C:\users\Martin\source\build\6SV\1.1\6SV1.1\sixsV1.1")


def setup_model(lat: float, date: str, ground_type=GroundReflectance.GreenVegetation, aot550=None):
    s = SixS(sixs_exe_path)
    s.ground_reflectance = GroundReflectance.HomogeneousLambertian(ground_type)
    s.atmos_profile = AtmosProfile.FromLatitudeAndDate(lat, date)
    if aot550 is not None:
        s.aot550 = aot550
    return s


def run_model(s: SixS):
    try:
        s.run()
        return s
    except Exception as e:
        logging.error("SixS model failed to run: %s", e)
        return None


def plot_spectrum(wavelengths, values, label, title):
    plt.figure(figsize=(8, 5))
    plt.plot(wavelengths, values, label=label)
    plt.xlabel("Wavelength (\u03bcm)")
    plt.ylabel("Radiance (W/m²/sr/μm)")
    plt.grid()
    plt.legend()
    plt.title(title)
    plt.show()


def main():
    latitude = 50
    date_str = "2024-07-14"

    # Initial run
    s = setup_model(latitude, date_str)
    s = run_model(s)
    if s is None:
        return

    logging.info("Apparent Reflectance: %s", s.outputs.apparent_reflectance)
    logging.info("Apparent Radiance: %s", s.outputs.apparent_radiance)
    logging.info("Water Vapour Transmittance (Downward): %s", s.outputs.transmittance_water.downward)

    # Landsat ETM simulation
    wavelengths, outputs = SixSHelpers.Wavelengths.run_landsat_etm(s, output_name='apparent_radiance')
    plot_spectrum(wavelengths, outputs, "Landsat ETM", "Landsat ETM Radiance")

    # AOT variation simulations
    s1 = setup_model(latitude, date_str, aot550=0.1)
    s1 = run_model(s1)
    s2 = setup_model(latitude, date_str, aot550=2.0)
    s2 = run_model(s2)

    if s1 and s2:
        w1, o1 = SixSHelpers.Wavelengths.run_vnir(s1, output_name="apparent_radiance")
        w2, o2 = SixSHelpers.Wavelengths.run_vnir(s2, output_name="apparent_radiance")
        plot_spectrum(w1, o1, "AOT = 0.1", "VNIR Radiance with AOT Variations")
        plt.plot(w2, o2, label="AOT = 2.0")
        plt.legend()
        plt.show()


if __name__ == "__main__":
    main()
