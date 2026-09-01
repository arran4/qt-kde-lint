#include "kxmlguiwindow.h"

class MyWindow : public KXmlGuiWindow {
public:
    MyWindow() {
        setupGUI();
    }
};

class MyOtherWindow : public QMainWindow {
public:
    MyOtherWindow() {
        menuBar()->addMenu("File");
        addToolBar("Main");
    }
};
