#pragma once

#include <QMainWindow>

QT_BEGIN_NAMESPACE namespace Ui { class MainWindow; } QT_END_NAMESPACE

namespace psu::ui {

class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void on_actionPSU_triggered();

private:
    Ui::MainWindow* ui_;
    int count_;
};

}
