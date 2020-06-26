from conans import ConanFile, CMake, tools
import os
import glob

class WindNinjaConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
   

    name = "windmapper"
    version = "0.1"
    
    generators = "cmake_find_package"

    options = {"openmp":[True, False]}

    default_options = {"openmp":False}
 

    def source(self):
        pass

    def requirements(self):
        self.requires( "windninja/3.5.3@CHM/stable" )

    def deploy(self):
        self.copy("*")  # copy from current package
        self.copy_deps("*.so*") # copy from dependencies
        self.copy_deps("*.dylib*") # copy from dependencies

    def imports(self):
        self.copy("*.so*", "lib", "lib")  # From bin to bin
        self.copy("*.dylib*", "lib", "lib")  # From lib to bin

        self.copy("*", "bin", "bin")  # From lib to bin
