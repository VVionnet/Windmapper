Use
===

Ensure the paths ``fic_config_WN`` and ``wn_exe`` are correctly set in
the configuration file.

WindMapper may be run in two modes:

1) download a SRTM tile that corresponds to a lat/long bounding box
   defined by the user or;
2) use a user-supplied DEM

The example given in ``examples/download_DEM`` can be run as

::

   python wind_mapper_generic.py examples/download_DEM/param_download_DEM.py
