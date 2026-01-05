cmake_minimum_required(VERSION 4.2.1)
project(psu)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PkgConfig REQUIRED)
pkg_check_modules(libserialport REQUIRED IMPORTED_TARGET libserialport)

option(BUILD_TESTING "Build tests or not" OFF)
if(BUILD_TESTING)
    enable_testing()
    find_package(Catch2 REQUIRED)
    include(Catch)
endif()

add_subdirectory(psu_core)
add_subdirectory(psu_dps150)

