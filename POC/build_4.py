from Py6S import *
s = SixS("C:\\users\\Martin\\source\\build\\6SV\\1.1\\6SV1.1\\sixsV1.1")
# Run for the whole range of wavelengths that 6S supports
wv, res = SixSHelpers.Wavelengths.run_whole_range(s, output_name='pixel_radiance')
# Do the same, but at a coarser resolution, so that it's quicker
wv, res = SixSHelpers.Wavelengths.run_whole_range(s, spacing=0.030, output_name='pixel_radiance')
# Run for the Landsat TM bands
wv, res = SixSHelpers.Wavelengths.run_landsat_tm(s, output_name='pixel_radiance')
wv, res = SixSHelpers.Wavelengths.run_landsat_tm(s, output_name='pixel_radiance')
# Plot the results, setting the y-axis label appropriately
SixSHelpers.Wavelengths.plot_wavelengths(wv, res, 'Pixel radiance ($W/m^2$)')
