#include "kxmlguiwindow.h"
#include "kmainwindow.h"

class QMenu {
public:
    QMenu* addMenu(const QString& title);
};

class MyWindow : public KXmlGuiWindow {
public:
    MyWindow() {
        QMenu menu;
        menu.addMenu("Submenu");
        setupGUI();
    }
};

class MyMainWindow : public KMainWindow {
public:
    MyMainWindow() {
        QMenu menu;
        menu.addMenu("Submenu");
        setupGUI();
    }
};
