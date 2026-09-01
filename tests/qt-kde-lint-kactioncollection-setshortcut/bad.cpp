namespace KStandardAction {
    class Action {};
    Action* open(void*, void*, void*);
}

class QAction {
public:
    void setShortcut(int shortcut);
    void setShortcuts(int shortcuts);
};

class KActionCollection {
public:
    QAction* addAction(const char* name);
    QAction* addAction(const char* name, QAction* action);
};

KActionCollection* actionCollection();

void test() {
    QAction* zoomIn = actionCollection()->addAction("zoom_in");
    zoomIn->setShortcut(1); // bad

    QAction* zoomOut = actionCollection()->addAction("zoom_out");
    zoomOut->setShortcuts(2); // bad

    QAction* act1 = new QAction();
    actionCollection()->addAction("act1", act1);
    act1->setShortcut(1); // bad, passed to addAction

    QAction* act2 = (QAction*)KStandardAction::open(nullptr, nullptr, actionCollection());
    act2->setShortcut(2); // bad, returned from KStandardAction with collection

    actionCollection()->addAction("act3", act1)->setShortcut(2); // bad, returned from addAction
}
