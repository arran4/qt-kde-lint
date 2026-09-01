class QAction {
public:
    void setShortcut(int shortcut);
    void setShortcuts(int shortcuts);
};

class KActionCollection {
public:
    QAction* addAction(const char* name);
    QAction* addAction(const char* name, QAction* action);
    void setDefaultShortcut(QAction* action, int shortcut);
    void setDefaultShortcuts(QAction* action, int shortcuts);
};

KActionCollection* actionCollection();

void test() {
    QAction* zoomIn = actionCollection()->addAction("zoom_in");
    actionCollection()->setDefaultShortcut(zoomIn, 1); // good

    QAction* normal = new QAction();
    normal->setShortcut(2); // good, not managed by KActionCollection
}
