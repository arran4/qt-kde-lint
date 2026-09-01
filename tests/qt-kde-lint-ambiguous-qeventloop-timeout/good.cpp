namespace {
class QObject {};

class QEventLoop : public QObject {
public:
    void quit();
    int exec();
};

class QTimer {
public:
    static void singleShot(int msec, const QObject *receiver, void (QEventLoop::*member)());
};

class Reply : public QObject {
public:
    void finished();
    int result();
};

template <typename Func>
void connect(QObject*, void (Reply::*)(), QEventLoop*, Func);

void use(int);

void launchWorkSafely(Reply* reply) {
    QEventLoop loop;
    bool finished = false;
    QTimer::singleShot(2000, &loop, &QEventLoop::quit);
    connect(reply, &Reply::finished, &loop, [&]() {
        finished = true;
        loop.quit();
    });
    loop.exec();

    if (finished) {
        use(reply->result());
    }
}
}
