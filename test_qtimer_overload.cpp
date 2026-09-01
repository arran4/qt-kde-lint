class QObject {
public:
    QObject* parent() const;
};

enum TimerType { CoarseTimer };

class QTimer {
public:
    template <typename Func>
    static void singleShot(int msec, Func functor);

    template <typename Func>
    static void singleShot(int msec, TimerType timerType, Func functor);

    template <typename Func>
    static void singleShot(int msec, const QObject *context, Func functor);

    template <typename Func>
    static void singleShot(int msec, TimerType timerType, const QObject *context, Func functor);
};

class MyClass : public QObject {
public:
    void doWork() {
        QTimer::singleShot(100, [this] {});
        QTimer::singleShot(100, CoarseTimer, [this] {});
        QTimer::singleShot(100, this, [this] {});
        QTimer::singleShot(100, CoarseTimer, this, [this] {});
    }
};
