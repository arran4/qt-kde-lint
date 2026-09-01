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

class MainWin : public KMainWindow {};

int main() {
    MainWin win;
    win.show();
    return 0;
}
