#include "kxmlguiwindow.h"

class MyWindow : public KXmlGuiWindow {
public:
    MyWindow() {
        menuBar()->addMenu("File");
        addToolBar("Main");
        setupGUI();
    }
};
