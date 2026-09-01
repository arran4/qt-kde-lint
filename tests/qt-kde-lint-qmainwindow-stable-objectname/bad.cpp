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

class BadKMainWindow : public KMainWindow {
public:
    BadKMainWindow() {
        auto *toolbar = addToolBar("Main"); // BAD

        auto *dock = new QDockWidget("Dock"); // BAD
        addDockWidget(1, dock);
    }
};

class BadNormalWindow : public QMainWindow {
public:
    BadNormalWindow() {
        auto *toolbar = addToolBar("Main"); // BAD
        saveState();
    }
};

class DirectWindow : public KXmlGuiWindow {
public:
    DirectWindow() {
        addToolBar("BadDirect"); // BAD
    }
};

void local_test() {
    QMainWindow w;
    auto t = w.addToolBar("Test"); // BAD
    w.saveState();
}

class RestoreWindow : public QMainWindow {
public:
    RestoreWindow() {
        auto *toolbar = addToolBar("Main"); // BAD
        restoreState();
    }
};

class MemberBadWindow : public KMainWindow {
public:
    MemberBadWindow() {
        this->m_toolbar = addToolBar("Main2"); // BAD
        m_dock = new QDockWidget("Dock2"); // BAD
    }
private:
    QToolBar* m_toolbar;
    QDockWidget* m_dock;
};
