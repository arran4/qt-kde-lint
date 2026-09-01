class QString {
public:
    QString(const char*);
};

class QObject {
public:
    void setObjectName(const QString&);
};


class QWidget : public QObject {};
class QMainWindow : public QWidget {
public:
    class QToolBar* addToolBar(const QString &title);
    void addToolBar(class QToolBar*);
    void addDockWidget(int, class QDockWidget*);
    void saveState();
    void restoreState();
};

class KMainWindow : public QMainWindow {};
class KXmlGuiWindow : public KMainWindow {};

class QToolBar : public QWidget {
public:
    QToolBar(const QString& title, QWidget *parent = nullptr);
    void setObjectName(const QString&);
};

class QDockWidget : public QWidget {
public:
    QDockWidget(const QString& title, QWidget *parent = nullptr);
    void setObjectName(const QString&);
};

class GoodKMainWindow : public KMainWindow {
public:
    GoodKMainWindow() {
        auto *toolbar = addToolBar("Main"); // GOOD
        toolbar->setObjectName("MainToolBar");

        auto *dock = new QDockWidget("Dock"); // GOOD
        dock->setObjectName("MainDock");
        addDockWidget(1, dock);
    }
};

class GoodNormalWindow : public QMainWindow {
public:
    GoodNormalWindow() {
        auto *toolbar = addToolBar("Main"); // GOOD, doesn't save state
    }
};

class GoodDirectWindow : public KXmlGuiWindow {
public:
    GoodDirectWindow() {
        addToolBar("GoodDirect")->setObjectName("OK"); // GOOD
    }
};

void local_test_good() {
    QMainWindow w;
    auto t = w.addToolBar("Test"); // GOOD
    t->setObjectName("TestBar");
    w.saveState();
}

class MemberGoodWindow : public QMainWindow {
public:
    MemberGoodWindow() {
        this->m_toolbar = addToolBar("Main2"); // GOOD
        this->m_toolbar->setObjectName("MainToolBar2");

        m_toolbar_no_this = addToolBar("Main3"); // GOOD
        m_toolbar_no_this->setObjectName("MainToolBar3");
    }
    void saveState();
private:
    QToolBar* m_toolbar;
    QToolBar* m_toolbar_no_this;
};

class IgnoreExistingToolbar : public KMainWindow {
public:
    IgnoreExistingToolbar() {
        QToolBar* existing = new QToolBar("Exist"); // GOOD (not a dockwidget or returned addToolBar)
        addToolBar(existing);
        existing->setObjectName("ExistBar");
    }
};
