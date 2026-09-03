namespace {
class QAction {
public:
    void triggered();
};
class QObject {
public:
    template <typename Func1, typename Func2>
    static void connect(QAction *sender, Func1 signal, QObject *receiver, Func2 slot) {}
};
class QUrl {};
class QContextMenuEvent {
public:
    QUrl url() const { return QUrl(); }
};
}

class Viewer : public QObject {
public:
    void contextMenuEvent(QContextMenuEvent *event) {
        mCurrentUrl = event->url(); // Assign transient state
        QAction *action = new QAction();
        // But the callback reads an unrelated stable setting, which is fine
        connect(action, &QAction::triggered, this, [this]() {
            use(mPersistentSetting);
        });
    }
    void use(int setting) {}
private:
    QUrl mCurrentUrl;
    int mPersistentSetting = 42;
};
