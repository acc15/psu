project(gui)

find_package(Qt6 REQUIRED COMPONENTS Widgets)
qt_standard_project_setup()
qt_add_executable(gui)

target_sources(gui PRIVATE 
    src/main.cpp
    src/mainwindow.cpp
    src/mainwindow.hpp
    src/mainwindow.ui
)

target_link_libraries(gui PRIVATE Qt6::Widgets)
