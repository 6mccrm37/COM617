from Py6S import *
s = SixS("C:\\users\\Martin\\source\\build\\6SV\\1.1\\6SV1.1\\sixsV1.1")
# Run for the whole range (takes a long time!)
wv, res = SixSHelpers.Wavelengths.run_landsat_tm(s)
# Look at what is in the results list - it should be an outputs instance
print(res[0])
# We can't do anything with the outputs instances directly, but lets
# extract some outputs - we can do all of this without having to run
# the whole simulation again, as the res variable is storing all of the
# outputs
refl = SixSHelpers.Wavelengths.extract_output(res, "pixel_reflectance")
rad = SixSHelpers.Wavelengths.extract_output(res, "pixel_radiance")
SixSHelpers.Wavelengths.plot_wavelengths(wv, refl, "Pixel reflectance")
SixSHelpers.Wavelengths.plot_wavelengths(wv, rad, "Pixel radiance")