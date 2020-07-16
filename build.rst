wind_mapper
===========

Wind_mapper is a tool used to produce pre-computed libraries of wind
field used for wind downscaling. Wind_mapper uses the
`WindNinja <https://github.com/firelab/windninja>`__ wind diagnostic
model. It has been primarily developped for wind downscaling for the
Canadian Hydrological Model `CHM <https://github.com/Chrismarsh/CHM>`__.

Installation
============

Base
----

WindMapper requires a python environment with the following packages
installed:

-  gdal
-  pyproj
-  numpy
-  scipy

It’s recommended these are installed in a virtual environment.

MacOS
-----

On macos, the gdal binaries should be installed from homebrew

::

   brew install gdal

and then the corresponding gdal-python package installed at the
corresponding version. For example:

::

   pip install gdal==2.4.2

WindNinja
---------

WindMapper depends upon WindNinja. This can be compiled from source, or
can be installed via conan.

.. _macos-1:

MacOs
~~~~~

Currently the MacOS OpenMP build of WindNinja does not work
https://github.com/firelab/windninja/issues/355

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
