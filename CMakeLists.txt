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
                KEEP_RPATHS
                SETTINGS compiler.cppstd=14
                SETTINGS compiler.libcxx=${CONAN_LIB_STD}
                INSTALL_FOLDER ${CMAKE_BINARY_DIR}
                NO_OUTPUT_DIRS
                BUILD missing
)

execute_process(
    COMMAND bash -c "otool -l ${CMAKE_BINARY_DIR}/bin/WindNinja_cli| grep name | grep -v segname | grep -v sectname |  grep -v /usr | grep -v /System | grep -v @rpath | awk '{print $2}' | while read x; do install_name_tool -change $x @rpath/`echo $x | grep -Eo '[a-zA-Z0-9_\.-]+\.dylib'` ${CMAKE_BINARY_DIR}/bin/WindNinja_cli; done"
)

install( DIRECTORY ${CMAKE_BINARY_DIR}/lib/
         DESTINATION ${CMAKE_INSTALL_PREFIX}/bin/lib/
)
install( DIRECTORY ${CMAKE_BINARY_DIR}/share/
         DESTINATION ${CMAKE_INSTALL_PREFIX}/bin/share/
)
install( PROGRAMS ${CMAKE_BINARY_DIR}/bin/WindNinja_cli
         DESTINATION ${CMAKE_INSTALL_PREFIX}/bin/bin/
)
