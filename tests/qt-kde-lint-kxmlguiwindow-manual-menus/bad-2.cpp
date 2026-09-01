#include "kmainwindow.h"

class MyMainWindow : public KMainWindow {
public:
    MyMainWindow() {
        menuBar()->addMenu("File");
        addToolBar("Main");
        setupGUI();
    }
};
