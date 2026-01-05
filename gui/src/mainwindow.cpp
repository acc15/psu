#include "mainwindow.hpp"
#include <QMessageBox>
#include "./ui_mainwindow.h"

namespace psu::gui {

MainWindow::MainWindow(QWidget *parent): 
    QMainWindow(parent), 
    ui(new Ui::MainWindow) 
{
    ui->setupUi(this);
}

MainWindow::~MainWindow() {
    delete ui;
}

void MainWindow::on_exitButton_clicked() {
    QMessageBox::information(this, "Information", "Application will close");
    QApplication::quit();
}

}