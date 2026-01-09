#include "mainwindow.hpp"
#include <QMessageBox>
#include <QDebug>
#include <QString>
#include <QDockWidget>
#include "./ui_mainwindow.h"

namespace psu::ui {

MainWindow::MainWindow(QWidget *parent): 
    QMainWindow(parent), 
    ui_(new Ui::MainWindow),
    count_(0)
{
    ui_->setupUi(this);
}

MainWindow::~MainWindow() {
    delete ui_;
}

void MainWindow::on_actionPSU_triggered() {
    QDockWidget* dock = new QDockWidget(QString("Hello %1").arg(++count_), this);
    dock->setAllowedAreas(Qt::AllDockWidgetAreas);
    addDockWidget(Qt::DockWidgetArea::RightDockWidgetArea, dock);
}


}
