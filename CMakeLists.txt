cmake_minimum_required(VERSION 4.2.1)
project(psu)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PkgConfig REQUIRED)
pkg_check_modules(libserialport REQUIRED libserialport)

add_library(psu_logic
    src/resource.hpp
    src/dps150.hpp
    src/dps150.cpp
    src/sp_utils.hpp
    src/sp_utils.cpp
)
target_include_directories(psu_logic PRIVATE ${libserialport_INCLUDE_DIRS})
target_link_libraries(psu_logic PRIVATE ${libserialport_LIBRARIES})

add_executable(psu
    src/main.cpp
)
target_link_libraries(psu PRIVATE psu_logic)

option(BUILD_TESTING "Build tests or not" OFF)
if(BUILD_TESTING)
    find_package(doctest REQUIRED)
    enable_testing()
    add_executable(psu_test
        tests/main.cpp
        tests/dps150.cpp
    )
    target_link_libraries(psu_test PRIVATE doctest::doctest psu_logic)
    target_include_directories(psu_test PRIVATE src)
    include(doctest) 
    doctest_discover_tests(psu_test)
endif()

