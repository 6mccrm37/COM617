from fastapi import FastAPI, Response, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from Py6S import *
from pathlib import Path
import logging
import csv
import os
from datetime import datetime
import sys

# Create FastAPI app first
app = FastAPI()

# Apply CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to ["http://localhost:8000"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(level=logging.INFO)

# Define the path to the sixs executable
sixs_exe_path = Path(r"C:\users\Martin\source\build\6SV\1.1\6SV1.1\sixsV1.1")

# Directory for saving CSVs
EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)

# Directory for serving WDC files
WDC_DIR = Path("wdc")
WDC_DIR.mkdir(exist_ok=True)

# Mount static WDC directory
app.mount("/wdc", StaticFiles(directory=WDC_DIR), name="wdc")

# Define input model for API
class Py6SParams(BaseModel):
    latitude: float
    date: str  # Format: YYYY-MM-DD
    aot550: float = None
    sensor: str = "landsat_etm"  # or "vnir"

# Core model setup function
def setup_model(lat: float, date: str, ground_type=GroundReflectance.GreenVegetation, aot550=None):
    logging.info(f"Running model with lat={lat}, date={date}, aot550={aot550}")
    s = SixS(sixs_exe_path)
    s.ground_reflectance = GroundReflectance.HomogeneousLambertian(ground_type)
    s.atmos_profile = AtmosProfile.FromLatitudeAndDate(lat, date)
    if aot550 is not None:
        s.aot550 = aot550
    return s

# Model runner function
def run_model(s: SixS, sensor: str):
    try:
        logging.info(f"Python exec path: {sys.executable}")
        logging.info(f"SixS path: {sixs_exe_path}")
        logging.info(f"SixS path exists: {sixs_exe_path.exists()}")
        logging.info("Attempting to run Py6S...")

        s.run()

        if s.outputs is None:
            logging.error("Py6S run completed but outputs are None. Possible input or SixS path error.")
            return {"error": "Py6S did not return any outputs. Please check your SixS executable or input parameters."}

        saved_outputs = s.outputs  # Save outputs before helper overwrites them
        logging.info("Py6S returned outputs: Reflectance = %s", saved_outputs.apparent_reflectance)

        if sensor == "landsat_etm":
            wavelengths, radiance = SixSHelpers.Wavelengths.run_landsat_etm(s, output_name='apparent_radiance')
        elif sensor == "vnir":
            wavelengths, radiance = SixSHelpers.Wavelengths.run_vnir(s, output_name='apparent_radiance')
        else:
            return {"error": "Unsupported sensor type"}

        return {
            "wavelengths": list(wavelengths),
            "radiance": list(radiance),
            "key_outputs": {
                "apparent_reflectance": float(saved_outputs.apparent_reflectance),
                "apparent_radiance": float(saved_outputs.apparent_radiance),
                "water_vapour_transmittance_downward": float(saved_outputs.transmittance_water.downward)
            }
        }
    except Exception as e:
        logging.error("Model failed: %s", e)
        return {"error": str(e)}

# API endpoint to run model
@app.post("/run-model")
def run_py6s_model(params: Py6SParams):
    model = setup_model(params.latitude, params.date, aot550=params.aot550)
    result = run_model(model, params.sensor)
    return result

# API endpoint to export results as CSV
@app.post("/export-csv")
def export_csv(params: Py6SParams):
    model = setup_model(params.latitude, params.date, aot550=params.aot550)
    result = run_model(model, params.sensor)

    if "error" in result:
        logging.warning("Model returned an error: %s", result["error"])
        return result

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"py6s_export_{timestamp}.csv"
    filepath = EXPORT_DIR / filename

    logging.info("Attempting to write CSV to: %s", filepath)

    # Write to CSV
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["wavelength", "radiance"])
        for wl, rad in zip(result["wavelengths"], result["radiance"]):
            writer.writerow([wl, rad])

    logging.info("Exported CSV to %s", filepath)

    return {"message": "CSV exported successfully", "file": str(filepath)}

# Serve WDC entrypoint
@app.get("/wdc/connector.html", response_class=HTMLResponse)
def serve_wdc():
    html_file = WDC_DIR / "connector.html"
    if html_file.exists():
        with open(html_file, "r") as f:
            return f.read()
    else:
        return HTMLResponse(content="<h1>WDC not found</h1>", status_code=404)
