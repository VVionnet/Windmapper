Use
===


WindMapper may be run in one of two modes:

1) download a SRTM tile that corresponds to a lat/long bounding box
   defined by the user or;
2) use a user-supplied DEM

Two examples are given, one for each use case. These are available in the source tree under ``examples``.

Download
---------
The example given in ``examples/download_DEM`` can be run as

::

   wind_mapper_generic.py examples/download_DEM/param_download_DEM.py

Existing
---------
The example given in ``examples/existing_DEM`` can be run as

::

   wind_mapper_generic.py examples/download_DEM/param_existing_DEM.py

Output
-------
Once Windmapper has run, the output folder will have a set of files:

.. confval:: ref-DEM-utm.tif

    The entire domain to be run on

.. confval:: tmp_X_Y.tif

    Windmapper tiles the domain to ensure a tractable solution. Each tile will be named tmp_X_Y.tif for example tmp_0_0.

.. confval:: ref-DEM-utm-*.vrt

    A VRT file is an xml meta-file that is a collection of underlying rasters that make up a larger raster. These underlying
    rasters are in the ``tmp_dir_X_Y`` directories. The number in the vrt name, e.g., 180 in ``ref-DEM-utm_180_V.vrt`` is the direction
    the wind comes from. The U/V refer to either the U or V component speedup. And the ``_spd_up_X`` suffix, e.g., ``_spd_up_1000``, is the
    wind speed (:math:`W=sqrt(U^2+V^2)`) with the given averaging distanced as specified in the configuration (1000 m default).

