namespace std {
template <typename T> class unique_ptr {
public:
    T* get() const { return ptr; }
    T* ptr;
};
}

template <typename T> class QScopedPointer {
public:
    T* get() const { return ptr; }
    T* ptr;
};

class QMenu {
public:
    QMenu();
};

class QSystemTrayIcon {
public:
    QSystemTrayIcon();
    void setContextMenu(QMenu *menu);
};

class MyTray {
    QMenu menu;
    std::unique_ptr<QMenu> menu_ptr;
    QSystemTrayIcon tray;

public:
    void setup1() {
        tray.setContextMenu(&menu);
    }
    void setup2() {
        tray.setContextMenu(menu_ptr.get());
    }
};

void test_heap() {
    QMenu *menu = new QMenu();
    QSystemTrayIcon trayIcon;
    trayIcon.setContextMenu(menu);
}

void test_global() {
    static QMenu global_menu;
    QSystemTrayIcon trayIcon;
    trayIcon.setContextMenu(&global_menu);
}
