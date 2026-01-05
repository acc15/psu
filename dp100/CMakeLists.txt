cmake_minimum_required(VERSION 4.2.1)
project(dp100)

find_package(hidapi REQUIRED)

add_library(dp100)
target_sources(dp100 PRIVATE 
    src/dp100.cpp
)
target_sources(dp100 PUBLIC FILE_SET HEADERS BASE_DIRS include FILES 
    include/psu/dp100.hpp 
)
target_link_libraries(dp100 PRIVATE core hidapi::hidapi)

if(BUILD_TESTING)
    add_executable(dp100_tests)
    target_sources(dp100_tests PRIVATE
        tests/dp100.cpp
    )
    target_link_libraries(dp100_tests PRIVATE Catch2::Catch2WithMain dp100)
    catch_discover_tests(dp100_tests)
endif()
