#include <QtCore/QPluginLoader>
#include <QtCore/QObject>

class Wrapper {
public:
    Wrapper(QObject *obj) {}
};

void foo() {
    QPluginLoader loader("plugin.so");
    auto *wrapper = new Wrapper(loader.instance());
    delete wrapper;
}
