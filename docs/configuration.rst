Configuration
==============

Windmapper depends heavily upon GDAL to handle the geospatial data. Any 1-band raster that GDAL can open is valid. Input rasters need to have a coordinate system.

.. warning::
    There cannot be missing data in the raster

.. note::
   Only the items in the `Required`_ section are needed for a valid configuration file.



Required
----------

Windmapper can be used in one of two modes:

1) With a user-supplied DEM (default)
2) With an automatically downloaded SRTM DEM based on user-provided bounding box.

User-supplied DEM
~~~~~~~~~~~~~~~~~~

.. confval:: use_existing_dem

    :default: true

    Use an existing DEM file. Requires `dem_filename` to be provided

.. confval:: dem_filename

    :type: string

    Absolute or relative path to the DEM to open. Any GDAL supported single-band raster is supported. Must have a coordinate system.

.. warning::

    A user-supplied DEM must be in UTM coordinates.

.. code:: python

    # Flag to use existing DEM (DEM must be in UTM for WindNinja)
    use_existing_dem = True

    # name of the DEM file if use_existing_dem = True
    dem_filename = '../data/srtm_snowcast.tif'

Downloaded DEM
~~~~~~~~~~~~~~~

Set `use_existing_dem` to be False. Then

.. confval:: lat_min

    Southern latitude bound

.. confval:: lat_max

    Northern latitude bound

.. confval:: lon_min

    Western longitude bound

.. confval:: long_max

    Eastern longitude bound

.. code:: python

    # Example for a region in the Jura, France
    lat_min = 46.5
    lat_max = 46.7
    lon_min = 5.80
    lon_max = 6.15

Optional
-----------

.. confval:: res_wind

    :default: 150 m

    Spatial  resolution of the WindNinja simulations

.. confval:: wn_exe

    :default: string

    Path to the WindNinja CLI executable `WindNinja_cli`. If Windmapper was installed via pip, then this does not need to be set.

.. confval:: ncat

    :default: 4

    Number of wind speed categories (every 360/ncat degrees)

.. confval:: fic_config_WN

    Path to WindNinja `cli_massSolver.cfg` file. By default, Windmapper produces this file on-demand. However, if
    extra customization is required, it can be specified by the user.

    The contents are:

.. code::

    #
    #	This is an example command line interface (cli) configuration file.
    #
    #	This particular file illustrates the necessary settings to
    #	for the mass conserving version of Wond Ninja
    #       See https://github.com/firelab/windninja for more details
    #
    #

    num_threads              = 4    # May be changed depending on the machine used to run WN
    initialization_method    = domainAverageInitialization
    units_mesh_resolution    = m
    input_speed              = 10.0
    input_speed_units        = mps
    input_wind_height        = 40.0
    units_input_wind_height  = m
    output_wind_height       = 40.0
    units_output_wind_height = m
    output_speed_units       = mps
    vegetation               = grass
    diurnal_winds            = false
    write_goog_output        = false
    write_shapefile_output   = false
    write_ascii_output       = true
    write_farsite_atm        = false


.. confval:: wind_average

    :default: 'grid'

    Averaging method to compute the transfer function in the downscaling method:
        - "mean_tile": the wind speed is average over the whole domain for each WN simulation (as in Marsh et al, 2020)
        - "grid": the wind speed is averaged over a squared area of size `targ_res` (as in Vionnet et al., 2020)

    Over domains of O(1 km^2 +), 'grid' should be used.

.. confval:: targ_res

    :default: 1000 m

    Used when `wind_average='grid'`, the windspeed is averaged over a squared area of size `targ_res`.

.. confval:: user_output_dir

    :type: string
    :default: ./configuration-script-name

    Output directory.