from Py6S import *
s = SixS("C:\\users\\Martin\\source\\build\\6SV\\1.1\\6SV1.1\\sixsV1.1")

for param in [AtmosProfile.Tropical, AtmosProfile.MidlatitudeSummer, AtmosProfile.MidlatitudeWinter]:
  s.atmos_profile = AtmosProfile.PredefinedType(param)
  s.run()
  print(s.outputs.pixel_radiance)