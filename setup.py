from skbuild import setup
import subprocess
from packaging.version import LegacyVersion
from skbuild.exceptions import SKBuildError
from skbuild.cmaker import get_cmake_version

def get_installed_gdal_version():
    try:
        version = subprocess.run(["gdal-config","--version"], stdout=subprocess.PIPE).stdout.decode()

        version = version.replace('\n', '')
        version = "=="+version+".*"
        return version
    except FileNotFoundError as e:
        raise(""" ERROR: Could not find the system install of GDAL. 
                  Please install it via your package manage of choice.
                """
            )

# Add CMake as a build requirement if cmake is not installed or is too low a version
# https://scikit-build.readthedocs.io/en/latest/usage.html#adding-cmake-as-building-requirement-only-if-not-installed-or-too-low-a-version
setup_requires = []
try:
    if LegacyVersion(get_cmake_version()) < LegacyVersion("3.16"):
        setup_requires.append('cmake')
except SKBuildError:
    setup_requires.append('cmake')


setup(name='windmapper',
      version='1.0.0',
      description='Windfield library generation',
      long_description="""
      Generates windfields
      """,
      author='Chris Marsh',
      author_email='chris.marsh@usask.ca',
      url="https://github.com/Chrismarsh/Windmapper",
      include_package_data=True,
      cmake_args=['-DCMAKE_BUILD_TYPE=Release'],
      scripts=["windmapper.py","cli_massSolver.cfg"],
      install_requires=['pygdal'+get_installed_gdal_version(),'numpy','scipy','elevation','pyproj'],
      setup_requires=setup_requires,
      python_requires='>=3.6'
     )