namespace Qt {
    enum WidgetAttribute {
        WA_DeleteOnClose = 55
    };
}
class QWidget {
public:
    void setAttribute(Qt::WidgetAttribute, bool on = true);
    void show();
};
class KMainWindow : public QWidget {};
class KXmlGuiWindow : public KMainWindow {};

class MainWindow : public KXmlGuiWindow {};

int main() {
    MainWindow window;
    MainWindow window2;
    window2.setAttribute(Qt::WA_DeleteOnClose, false);
    window.show();
    return 0;
}
