#include "qstring.h"

namespace {
class QGuiApplication {
public:
    static void setDesktopFileName(const QString &name);
};
}

void test() {
    QGuiApplication::setDesktopFileName("org.example.App"); // good
}
