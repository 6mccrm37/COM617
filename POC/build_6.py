from Py6S import *
s = SixS("C:\\users\\Martin\\source\\build\\6SV\\1.1\\6SV1.1\\sixsV1.1")
# Set the ground reflectance to have some sort of BRDF, or the plot will
# be really boring! In this case, we're using the Roujean model
s.ground_reflectance = GroundReflectance.HomogeneousRoujean(0.037, 0.0, 0.133)
# Run the model and plot the results, varying the view angle (the other
#  option is to vary the solar angle) and plotting the pixel reflectance.
SixSHelpers.Angles.run_and_plot_360(s, 'view', 'pixel_reflectance')
