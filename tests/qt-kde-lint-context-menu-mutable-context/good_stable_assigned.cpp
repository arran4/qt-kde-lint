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
}

class Viewer : public QObject {
public:
    int loadSetting() { return 42; }

    void init() {
        mPersistentSetting = loadSetting();
        QAction *action = new QAction();
        connect(action, &QAction::triggered, this, [this]() {
            use(mPersistentSetting);
        });
    }

    void use(int setting) {}

private:
    int mPersistentSetting;
};
