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

void test_local_stack() {
    QMenu menu;
    QSystemTrayIcon trayIcon;
    trayIcon.setContextMenu(&menu);
}

void test_unique_ptr() {
    std::unique_ptr<QMenu> menu;
    QSystemTrayIcon trayIcon;
    trayIcon.setContextMenu(menu.get());
}

void test_scoped_pointer() {
    QScopedPointer<QMenu> menu;
    QSystemTrayIcon trayIcon;
    trayIcon.setContextMenu(menu.get());
}
