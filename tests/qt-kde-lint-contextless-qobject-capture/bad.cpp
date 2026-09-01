class QObject {
public:
    QObject* parent() const;
};

class QTimer {
public:
    template <typename Func>
    static void singleShot(int msec, Func functor);

    template <typename Func>
    static void singleShot(int msec, const QObject *context, Func functor);
};

namespace QtConcurrent {
    template <typename Func>
    void run(Func function);
}

class MyClass : public QObject {
public:
    void doWork() {
        // Bad: implicit this capture of QObject
        QTimer::singleShot(100, [this] {
            // CHECK-MESSAGES: :[[@LINE-1]]:33: warning: This deferred functor captures a raw QObject pointer but has no QObject lifetime context. [custom-qt-kde-lint-contextless-qobject-capture]
            this->parent();
        });

        QObject* obj = new QObject();
        // Bad: capturing local QObject pointer contextlessly
        QTimer::singleShot(100, [obj] {
            // CHECK-MESSAGES: :[[@LINE-1]]:33: warning: This deferred functor captures a raw QObject pointer but has no QObject lifetime context. [custom-qt-kde-lint-contextless-qobject-capture]
            obj->parent();
        });

        // Bad: capturing this contextlessly in QtConcurrent::run
        QtConcurrent::run([this] {
            // CHECK-MESSAGES: :[[@LINE-1]]:27: warning: This deferred functor captures a raw QObject pointer but has no QObject lifetime context. [custom-qt-kde-lint-contextless-qobject-capture]
            this->parent();
        });

        QObject& objRef = *this;
        // Bad: capturing QObject reference contextlessly
        QtConcurrent::run([&objRef] {
            // CHECK-MESSAGES: :[[@LINE-1]]:27: warning: This deferred functor captures a raw QObject pointer but has no QObject lifetime context. [custom-qt-kde-lint-contextless-qobject-capture]
            objRef.parent();
        });
    }
};
