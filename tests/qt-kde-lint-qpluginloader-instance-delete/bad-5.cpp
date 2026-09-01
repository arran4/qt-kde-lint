#include <QtCore/QPluginLoader>
#include <QtCore/QObject>

class Interface : public QObject {};

void foo() {
    QPluginLoader loader("plugin.so");
    Interface *plugin = dynamic_cast<Interface *>(loader.instance());
    delete plugin;
}
