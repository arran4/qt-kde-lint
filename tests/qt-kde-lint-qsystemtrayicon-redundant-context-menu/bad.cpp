class QObject {};

class QMenu {
public:
    void popup(int pos) {}
    void exec() {}
};

class QCursor {
public:
    static int pos() { return 0; }
};

class QSystemTrayIcon : public QObject {
public:
    enum ActivationReason {
        Unknown,
        Context,
        DoubleClick,
        Trigger,
        MiddleClick
    };
    void setContextMenu(class QMenu* menu) {}
    void activated(ActivationReason reason) {}
};

class MyClass : public QObject {
public:
    template <typename Func1, typename Func2>
    static void connect(const QObject *sender, Func1 signal, const QObject *receiver, Func2 slot) {}

    template <typename Func1, typename Func2>
    static void connect(const QObject *sender, Func1 signal, Func2 slot) {}

    void setupTray() {
        QSystemTrayIcon* trayIcon = new QSystemTrayIcon();
        QMenu* trayMenu = new QMenu();

        trayIcon->setContextMenu(trayMenu);

        connect(trayIcon, 0, this,
                [trayMenu](QSystemTrayIcon::ActivationReason reason) {
                    if (reason == QSystemTrayIcon::Context) {
                        trayMenu->popup(QCursor::pos());
                    }
                });
    }

    void setupTray2() {
        QSystemTrayIcon* trayIcon = new QSystemTrayIcon();
        QMenu* trayMenu = new QMenu();

        trayIcon->setContextMenu(trayMenu);

        connect(trayIcon, 0, this,
                [trayMenu](QSystemTrayIcon::ActivationReason reason) {
                    switch (reason) {
                        case QSystemTrayIcon::Context:
                            trayMenu->exec();
                            break;
                        default:
                            break;
                    }
                });
    }
};
