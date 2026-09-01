#include "kxmlguiwindow.h"

class MyWindow : public KXmlGuiWindow {
public:
    MyWindow();
};

MyWindow::MyWindow() {
    menuBar()->addMenu("File");
    addToolBar("Main");
    setupGUI();
}
