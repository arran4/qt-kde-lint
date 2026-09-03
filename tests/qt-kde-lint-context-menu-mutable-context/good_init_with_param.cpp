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
class Settings {
public:
    int value() const { return 42; }
};
}

class Viewer : public QObject {
public:
    void init(Settings settings) {
        mPersistentSetting = settings.value();
        QAction *action = new QAction();
        connect(action, &QAction::triggered, this, [this]() {
            use(mPersistentSetting);
        });
    }

    void use(int setting) {}

private:
    int mPersistentSetting;
};
