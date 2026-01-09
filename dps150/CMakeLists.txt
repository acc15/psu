cmake_minimum_required(VERSION 4.2.1)
project(dps150)

find_package(PkgConfig REQUIRED)
pkg_check_modules(libserialport REQUIRED IMPORTED_TARGET libserialport)

add_library(dps150)

target_sources(dps150 PUBLIC FILE_SET HEADERS BASE_DIRS include FILES 
    include/psu/dps150/dps150.hpp 
)
target_sources(dps150 PRIVATE 
    src/dps150.cpp
    src/sp_utils.cpp
    src/sp_utils.hpp 
)

target_link_libraries(dps150 PRIVATE core PkgConfig::libserialport)

if(BUILD_TESTING)
    add_executable(dps150_tests)
    target_sources(dps150_tests PRIVATE
        tests/dps150.cpp
    )
    target_link_libraries(dps150_tests PRIVATE Catch2::Catch2WithMain dps150)
    catch_discover_tests(dps150_tests)
endif()
