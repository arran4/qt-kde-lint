class QModelIndex {};
class QPersistentModelIndex {
public:
    QPersistentModelIndex(QModelIndex);
};
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
    QPersistentModelIndex pIndex(index);
    QObject::connect(action, nullptr, nullptr, [pIndex]() {
        // use pIndex
    });
}

void testTimer(QModelIndex index) {
    QPersistentModelIndex pIndex(index);
    QTimer::singleShot(0, [pIndex]() {
        // use pIndex
    });
}
