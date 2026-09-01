class QThread {
public:
  template <typename Function> static QThread *create(Function &&function) {
    (void)function;
    return nullptr;
  }

  void start();
};

QThread *makeThread();

void retainedCreatedThread() {
  QThread *thread = QThread::create([] {});
  if (thread) {
    thread->start();
  }
}

void ordinaryThread() {
  QThread thread;
  thread.start();
}

void unrelatedFactory() { makeThread()->start(); }
