cmake_minimum_required(VERSION 4.2.1)
project(psu)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

option(BUILD_TESTING "Build tests or not" OFF)
if(BUILD_TESTING)
    enable_testing()
    find_package(Catch2 REQUIRED)
    include(Catch)
endif()

add_subdirectory(core)
add_subdirectory(dps150)
add_subdirectory(dp100)
add_subdirectory(ui)

