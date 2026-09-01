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
    MainWindow* window = new MainWindow;
    window->show();
    return 0;
}
