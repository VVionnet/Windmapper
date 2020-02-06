# wind_mapper

Wind_mapper is a tool used to produce pre-computed libraries of wind field used for wind downscaling. Wind_mapper uses the [WindNinja](https://github.com/firelab/windninja) wind diagnostic model. It has been primarily developped for wind downscaling for the Canadian Hydrological Model [CHM](https://github.com/Chrismarsh/CHM).  


# Installation

## Base
WindMapper requires a python environment with the following packages installed:

* gdal
* pyproj
* numpy
* scipy

It's recommended these are installed in a virtual environment. 

## MacOS 
On macos, the gdal binaries should be installed from homebrew
```
brew install gdal
```

and then the corresponding gdal-python package installed at the corresponding version. For example:
```
pip install gdal==2.4.2
```

## WindNinja
WindMapper depends upon WindNinja. This can be compiled from source, or can be installed via conan. 

```


```



## Installation of WindNinja

# Use
