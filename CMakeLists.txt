cmake_minimum_required(VERSION 3.16)
project(windmapper)

if(NOT EXISTS "${CMAKE_BINARY_DIR}/conan.cmake")

    message(STATUS "Downloading conan.cmake from https://github.com/conan-io/cmake-conan")
    file(DOWNLOAD "https://github.com/conan-io/cmake-conan/raw/v0.15/conan.cmake"
            "${CMAKE_BINARY_DIR}/conan.cmake")
endif()
include(${CMAKE_BINARY_DIR}/conan.cmake)

if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
    set(CONAN_LIB_STD "libstdc++11")
    message(STATUS "Detected gnu compiler, setting compiler.libcxx=${CONAN_LIB_STD}")
elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang" OR "${CMAKE_CXX_COMPILER_ID}" STREQUAL "AppleClang")
    set(CONAN_LIB_STD "libc++")
    message(STATUS "Detected clang compiler, setting compiler.libcxx=${CONAN_LIB_STD}")
endif ()

conan_add_remote(NAME CHM
        URL https://api.bintray.com/conan/chrismarsh/CHM
        )

conan_cmake_run(CONANFILE conanfile.py
                BASIC_SETUP
                SETTINGS compiler.cppstd=14
                SETTINGS compiler.libcxx=${CONAN_LIB_STD}
                INSTALL_FOLDER ${CMAKE_BINARY_DIR}
                NO_OUTPUT_DIRS
                BUILD missing
)

#conan_cmake_run(CONANFILE conanfile.py
#                SETTINGS compiler.cppstd=14
#                SETTINGS compiler.libcxx=${CONAN_LIB_STD}
#                BASIC_SETUP
#                CMAKE_TARGETS
#               KEEP_RPATHS
#                NO_OUTPUT_DIRS
#               INSTALL_FOLDER ${CMAKE_INSTALL_PREFIX}
#                BUILD missing)

install( DIRECTORY ${CMAKE_BINARY_DIR}/lib/
         DESTINATION ${CMAKE_INSTALL_PREFIX}/bin/lib/
)
install( PROGRAMS ${CMAKE_BINARY_DIR}/bin/WindNinja_cli
         DESTINATION ${CMAKE_INSTALL_PREFIX}/bin/bin/
)
