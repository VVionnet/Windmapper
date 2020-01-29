# Configuration file for windmapper when a DEM is downloaded from the SRTM 30m archive

# Resolution of WindNinja simulations (in m)
res_wind = 150

# File containing WN configuration
fic_config_WN ='../../cli_massSolver.cfg'

#Path to WindNinja (command line) executable
wn_exe = '/home/vvionnet/Code/WindNinja_CFD/windninja_exe/bin/WindNinja_cli'

# Number of wind speed categories (every 360/ncat degrees)
ncat = 2

# Flag to use existing DEM (DEM must be in UTM for WindNinja)
use_existing_dem = False

# If an existing DEM is not provided, the bounding box in lat lon must be provided
# Example for a region in the Jura, France
lat_min = 46.5
lat_max = 46.7
lon_min = 5.80
lon_max = 6.15

# Averaging method to compute the transfert function
wind_average = 'grid'

#Target resolution for avegaging (in m)
targ_res = 1000 #

# Output directory
#user_output_dir='/home/vvionnet/data3/Run_WindNinja/test_wn_dl'
