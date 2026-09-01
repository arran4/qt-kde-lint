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

void connect(QObject*, void (Reply::*)(), QEventLoop*, void (QEventLoop::*)());
void use(int);

void launchWork(Reply* reply) {
    QEventLoop loop;
    QTimer::singleShot(2000, &loop, &QEventLoop::quit);
    connect(reply, &Reply::finished, &loop, &QEventLoop::quit);
    loop.exec();

    use(reply->result());
}
}
