cmake_minimum_required(VERSION 4.2.1)
project(psu_dps150)

add_library(psu_dps150)
target_sources(psu_dps150 PRIVATE 
    src/dps150.cpp
    src/sp_utils.cpp
    src/sp_utils.hpp 
)
target_sources(psu_dps150 PUBLIC FILE_SET HEADERS BASE_DIRS include FILES 
    include/psu/dps150.hpp 
)
target_link_libraries(psu_dps150 PRIVATE psu_core PkgConfig::libserialport)

if(BUILD_TESTING)
    add_executable(psu_dps150_tests)
    target_sources(psu_dps150_tests PRIVATE
        tests/dps150.cpp
    )
    target_link_libraries(psu_dps150_tests PRIVATE Catch2::Catch2WithMain psu_dps150)
    catch_discover_tests(psu_dps150_tests)
endif()
