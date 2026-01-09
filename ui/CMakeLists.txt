project(ui)

find_package(Qt6 REQUIRED COMPONENTS Widgets)
qt_standard_project_setup()
qt_add_executable(ui)

target_sources(ui PRIVATE 
    src/main.cpp
    src/mainwindow.cpp
    src/mainwindow.hpp
    src/mainwindow.ui
)

target_link_libraries(ui PRIVATE Qt6::Widgets)
