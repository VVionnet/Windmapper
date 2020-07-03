Install
=========
.. note::

    Windmapper is only supported on Linux and MacOS. Python >= 3.6


Setup Python environment
-------------------------
It is recommended that Windmapper be installed into a Python3 virtual environment. This can be via conda, pyenv, or
venv. For example:

::

    python -m venv /path/to/new/virtual/environment

Install gdal
---------------
Ensure gdal libraries are installed.

Linux
******
On linux, depending on the distro used, you may need to also install the gdal binaries. On Ubuntu this is
::

   sudo apt-get install libgdal-dev
   sudo apt-get install gdal-bin
   sudo apt-get install python-gdal

MacOS
******
On MacOS, homebrew should be used to install gdal. Macport based installs likely work, but have not been tested.

On MacOS, the gdal binaries should be installed from homebrew

::

   brew install gdal


Install Windmapper
--------------------
Activate the venv created in step 1, and then install windmapper.

::

    pip install windmapper