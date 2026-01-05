project(gui)

find_package(Qt6 REQUIRED COMPONENTS Widgets)
qt_standard_project_setup()
qt_add_executable(gui)

target_sources(gui PRIVATE 
    src/main.cpp
)

target_link_libraries(gui PRIVATE Qt6::Widgets)
