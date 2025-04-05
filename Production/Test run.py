from Py6S import *
from pathlib import Path

sixs_path = Path(r"C:\users\Martin\source\build\6SV\1.1\6SV1.1\sixsV1.1")
s = SixS(sixs_path)
s.atmos_profile = AtmosProfile.FromLatitudeAndDate(50, "2024-07-14")
s.ground_reflectance = GroundReflectance.HomogeneousLambertian(GroundReflectance.GreenVegetation)
s.run()

print(s.outputs)  # Should NOT be None
