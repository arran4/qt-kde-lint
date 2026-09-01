class QWidget {};
class QWindow {};
class QDialog : public QWidget {};
class QMainWindow : public QWidget {};
class KMainWindow : public QMainWindow {};
class KXmlGuiWindow : public KMainWindow {};

class QThread {
public:
    static void sleep(unsigned long);
    static void msleep(unsigned long);
    static void usleep(unsigned long);
};
class QEventLoop {
public:
    int exec(int flags = 0);
};

class MyWidget : public QWidget {
public:
    void bad() {
        QThread::sleep(1);
        QThread::msleep(2);
        QThread::usleep(3);
        QEventLoop loop;
        loop.exec();
    }
};

class MyWindow : public QWindow {
public:
    void bad() {
        QThread::msleep(2);
    }
};

class MyDialog : public QDialog {
public:
    void bad() {
        QEventLoop loop;
        loop.exec();
    }
};

class MyMainWindow : public KXmlGuiWindow {
public:
    void bad() {
        QThread::usleep(3);
    }
};
