#include <QApplication>
#include <QPushButton>
#include <QWidget>
#include <QVBoxLayout>

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    QWidget window;
    window.setWindowTitle("Qt 2026 App");
    window.resize(300, 200);

    QVBoxLayout *layout = new QVBoxLayout(&window);
    QPushButton *button = new QPushButton("Hello Qt!", &window);
    
    layout->addWidget(button);
    window.show();

    return app.exec();
}