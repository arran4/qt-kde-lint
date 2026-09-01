class QThread {
public:
  template <typename Function> static QThread *create(Function &&function) {
    (void)function;
    return nullptr;
  }

  void start();
};

void launchWork() { QThread::create([] {})->start(); }
