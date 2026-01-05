cmake_minimum_required(VERSION 4.2.1)
project(core)

find_package(PkgConfig REQUIRED)
pkg_check_modules(libserialport REQUIRED IMPORTED_TARGET libserialport)

add_library(core INTERFACE)

target_sources(core PUBLIC FILE_SET HEADERS BASE_DIRS include FILES 
    include/psu/utils.hpp
)

target_link_libraries(core INTERFACE PkgConfig::libserialport)