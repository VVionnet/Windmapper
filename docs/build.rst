Build
======

Linux and MacOS are the only supported environments.
Python >= 3.6


Setup Python environment
-------------------------
It is recommended that Windmapper be installed into a Python3 virtual environment. 

If a system python3 isn't available, it can be easily installed and managed using `pyenv <https://github.com/pyenv/pyenv>`_:

::

   pyenv install 3.7.6
   pyenv shell 3.7.6 # activate this version of python for this shell


If ``pyenv`` is used, then the excellent `pyenv-virtualenv <https://github.com/pyenv/pyenv-virtualenv>`_ wrapper can easily streamline ``virtualenv`` creation 
::

   pyenv virtualenv 3.7.6 mesher-3.7.6
   pyenv activate mesher-3.7.6


Regardless of how the virtualenv is created, ``pip install`` the following packages:

::

   pip install elevation
   pip install pygdal=="`gdal-config --version`.*"
   pip install pyproj

The ``numpy`` and ``scipy`` packages are required but will be installed via ``pygdal``. 

It's recommended that gdal python bindings are installed via `pygdal <https://github.com/nextgis/pygdal>`_ as this approach is more robust when used with virtualenvs. gdal doesn't provide wheels, so ``pygdal`` will need to build from source. Therefore ensure gdal development files (e.g., ``gdal-devel``) are installed through your system's package manager. 

.. note::
   The python gdal bindings uses a system-wide gdal so ensure this installed via package manager/homebrew

On linux, depending on the distro used, you may need to also install the gdal binaries. On Ubuntu this is
::

   sudo apt-get install libgdal-dev
   sudo apt-get install gdal-bin
   sudo apt-get install python-gdal

The system gdal binaries such as ``gdalwarp`` are only available in the ``gdal-bin`` package. On linux, the gdal python bindings are required to install the python gdal scripts. However, the ``pygdal`` will be correctly used in the virtual environment.

On MacOS, homebrew should be used to install gdal. Macport based installs likely work, but have not been tested. 

On MacOS, the gdal binaries should be installed from homebrew

::

   brew install gdal


WindNinja
-----------
Windmapper depends on the `WindNinja <https://github.com/firelab/windninja>`__ program to compute the windfields. WindNinja may be installed separately, or it can be built and installed via Conan. These instructions will show how to do so via Conan. If a user-provided WindNinja install is used, this can be set in the configuration file.


- conan >= 1.21
- cmake >= 3.16
- C++11 compiler (gcc 7.x+ recommended)

Setup conan
***********

Install conan

::

   pip install conan

If cmake is not installed system wide:

::

   pip install cmake

or install via system package manager.

Initialize a new conan profile (if required)

::

    conan profile new default --detect
    conan remote add bincrafters https://api.bintray.com/conan/bincrafters/public-conan
    conan remote add CHM https://api.bintray.com/conan/chrismarsh/CHM
    conan profile update settings.compiler.cppstd=14 default  


conan needs to be told to use new C++11 ABI. If using clang (e.g., MacOs), do
::

    conan profile update settings.compiler.libcxx=libc++ default  #with clang


and if using gcc, do
::

    conan profile update settings.compiler.libcxx=libstdc++11 default  #with gcc


If you change compilers, such as on a cluster with a modules system, you can rerun 
::
    
    conan profile new default --detect --force


to detect the new compiler settings. The ``cppstd`` and ``libcxx`` settings need to be reapplied once this is done.

and then install WindNinja from Conan

::
    mkdir /opt/windninja && cd /opt/windninja #this could be any directory you wish to install to
    conan install windninja/3.5.3@CHM/stable -g deploy

.. note::

   Currently the MacOS OpenMP build of WindNinja does not work
   https://github.com/firelab/windninja/issues/355