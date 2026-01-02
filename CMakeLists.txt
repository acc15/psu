cmake_minimum_required(VERSION 4.2.1)
project(psu)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PkgConfig REQUIRED)
pkg_check_modules(libserialport REQUIRED IMPORTED_TARGET libserialport)

add_library(psu_logic
    src/utils.hpp
    src/dps150.hpp
    src/dps150.cpp
    src/sp_utils.hpp
    src/sp_utils.cpp
)
target_link_libraries(psu_logic PkgConfig::libserialport)

add_executable(psu
    src/main.cpp
)
target_link_libraries(psu PRIVATE psu_logic)

option(BUILD_TESTING "Build tests or not" OFF)
if(BUILD_TESTING)
    enable_testing()    
    find_package(Catch2 REQUIRED)
    add_executable(psu_tests
        tests/dps150.cpp
    )
    target_link_libraries(psu_tests PRIVATE Catch2::Catch2WithMain psu_logic)
    target_include_directories(psu_tests PRIVATE src)
    include(Catch)
    catch_discover_tests(psu_tests)
endif()

