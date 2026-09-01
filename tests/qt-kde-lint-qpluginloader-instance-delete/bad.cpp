#include <QtCore/QPluginLoader>
#include <QtCore/QObject>

void foo() {
    QPluginLoader loader("plugin.so");
    QObject *plugin = loader.instance();
    loader.unload();
    delete plugin;
}
