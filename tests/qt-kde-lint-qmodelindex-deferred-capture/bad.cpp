class QModelIndex {};
class QTimer {
public:
    template <typename Func>
    static void singleShot(int msec, Func slot) {}
};

struct QAction {};
struct QObject {
    template <typename Func>
    static void connect(QAction* sender, void* signal, void* context, Func slot) {}
};

void testAction(QAction* action, QModelIndex index) {
    QObject::connect(action, nullptr, nullptr, [index]() {
        // use index
    });
}

void testTimer(QModelIndex index) {
    QTimer::singleShot(0, [index]() {
        // use index
    });
}

void testActionRef(QAction* action, const QModelIndex& index) {
    QObject::connect(action, nullptr, nullptr, [index]() {
        // use index
    });
}
