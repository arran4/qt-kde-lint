#pragma once
#include "qstring.h"
class QMenu;
class QToolBar;
class QMenuBar;
class QMainWindow {
public:
    QMenuBar* menuBar() const;
    QToolBar* addToolBar(const QString& title);
};

class QMenuBar {
public:
    QMenu* addMenu(const QString& title);
};
