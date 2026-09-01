class QObject {
public:
    QObject* parent() const;
};

template <typename T>
class QPointer {
public:
    QPointer(T* p) : p_(p) {}
    T* operator->() const { return p_; }
    operator bool() const { return p_ != nullptr; }
private:
    T* p_;
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

class NonQObject {
public:
    void doWork() {
        QTimer::singleShot(100, [this] {
            // Contextless capture of 'this' is fine if 'this' is not a QObject.
        });

        NonQObject* obj = this;
        QtConcurrent::run([obj] {
            // Contextless capture of non-QObject pointer.
        });
    }
};

class MyClass : public QObject {
public:
    void doWork() {
        // Good: using context overload
        QTimer::singleShot(100, this, [this] {
            this->parent();
        });

        // Good: using QPointer with contextless overload
        QPointer<MyClass> weakThis(this);
        QTimer::singleShot(100, [weakThis] {
            if (weakThis) {
                weakThis->parent();
            }
        });

        // Good: capturing by value (structurally distinct from pointer/reference, though typically QObject is not copyable)
        // We include this to ensure we don't accidentally over-match by value capture.
        QObject obj;
        QTimer::singleShot(100, [obj] {

        });
    }
};
