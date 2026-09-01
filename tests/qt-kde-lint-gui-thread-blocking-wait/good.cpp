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
    static void fine_static() {
        QThread::sleep(1);
    }
};

class NonWidget {
public:
    void fine_not_widget() {
        QThread::sleep(1);
        QEventLoop loop;
        loop.exec();
    }
};
