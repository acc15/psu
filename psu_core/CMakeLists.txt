cmake_minimum_required(VERSION 4.2.1)
project(psu_core)

add_library(psu_core INTERFACE)

target_sources(psu_core PUBLIC FILE_SET HEADERS BASE_DIRS include FILES 
    include/psu/utils.hpp
)

target_link_libraries(psu_core INTERFACE PkgConfig::libserialport)