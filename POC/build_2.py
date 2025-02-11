from Py6S import *
s = SixS("C:\\users\\Martin\\source\\build\\6SV\\1.1\\6SV1.1\\sixsV1.1")
s.atmos_profile = AtmosProfile.UserWaterAndOzone(3.6, 0.9) # Set the atmosphere profile to be based on 3.6cm of water and 0.9cm-atm of ozone
s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_TM_B3) # Set the wavelength to be that of the Landsat TM Band 3 - includes response function
s.ground_reflectance = GroundReflectance.HomogeneousWalthall(1.08, 0.48, 4.96, 0.5) # Set the surface to have a BRDF approximated by the Walthall model
s.geometry = Geometry.Landsat_TM()
s.geometry.month = 7
s.geometry.day = 14
s.geometry.gmt_decimal_hour = 7.75
s.geometry.latitude = 51.148
s.geometry.longitude = 0.307
s.run()
print(s.outputs.pixel_radiance)