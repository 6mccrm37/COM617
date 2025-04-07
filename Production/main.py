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
    allow_origins=["*"],
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
    aot550_values: List[float]  # Accepts a list of AOT values
    sensor: str = "landsat_etm"  # or "vnir"

# Utility to write results to CSV
def write_csv(data, filename_prefix="py6s_export"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"
    filepath = EXPORT_DIR / filename

    logging.info("Writing CSV to: %s", filepath)

    with open(filepath, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["wavelength", "radiance", "aot550"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    return str(filepath)

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
    s.run()
    if s.outputs is None:
        raise RuntimeError("Py6S returned no output")

    saved_outputs = s.outputs

    if sensor == "landsat_etm":
        wavelengths, radiance = SixSHelpers.Wavelengths.run_landsat_etm(s, output_name='apparent_radiance')
    elif sensor == "vnir":
        wavelengths, radiance = SixSHelpers.Wavelengths.run_vnir(s, output_name='apparent_radiance')
    else:
        raise ValueError("Unsupported sensor type")

    return {
        "wavelengths": list(wavelengths),
        "radiance": list(radiance),
        "apparent_reflectance": float(saved_outputs.apparent_reflectance),
        "apparent_radiance": float(saved_outputs.apparent_radiance),
        "water_vapour_transmittance_downward": float(saved_outputs.transmittance_water.downward)
    }

# New endpoint for multiple simulations
@app.post("/run-multi")
def run_multi_endpoint(params: Py6SParams):
    all_results = []

    for aot in params.aot550_values:
        try:
            model = setup_model(params.latitude, params.date, aot550=aot)
            result = run_model(model, params.sensor)

            for wl, rad in zip(result["wavelengths"], result["radiance"]):
                all_results.append({
                    "wavelength": wl,
                    "radiance": rad,
                    "aot550": aot
                })
        except Exception as e:
            logging.error(f"Failed for AOT={aot}: {e}")
            continue

    csv_path = write_csv(all_results)
    return {"data": all_results, "csv_file": csv_path}

# API endpoint to export results as CSV
@app.post("/export-csv")
def export_csv(params: Py6SParams):
    all_results = run_multi_endpoint(params)["data"]
    csv_path = write_csv(all_results)
    return {"message": "CSV exported successfully", "file": csv_path}

# Serve WDC entrypoint
@app.get("/wdc/connector.html", response_class=HTMLResponse)
def serve_wdc():
    html_file = WDC_DIR / "connector.html"
    if html_file.exists():
        with open(html_file, "r") as f:
            return f.read()
    else:
        return HTMLResponse(content="<h1>WDC not found</h1>", status_code=404)

# Health check route
@app.get("/")
def root():
    return {"status": "ok", "message": "Py6S FastAPI backend running"}

# Version info
VERSION = "0.1.0"
@app.get("/version")
def version():
    return {"version": VERSION}
