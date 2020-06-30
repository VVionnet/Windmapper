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

1) With a user-supplied DEM
2) With an automatically downloaded SRTM DEM based on user-provided bounding box.

