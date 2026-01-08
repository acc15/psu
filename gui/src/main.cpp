#include <QApplication>
#include "mainwindow.hpp"

int main(int argc, char *argv[]) {
#ifdef __linux__
    qputenv("QT_QPA_PLATFORM", "xcb");
#endif
    
    QApplication app(argc, argv);
    psu::ui::MainWindow window;
    window.show();
    return app.exec();
}