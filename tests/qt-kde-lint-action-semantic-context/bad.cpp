class QString {
public:
    QString(const char*);
};

class QObject {};

class QAction {
public:
    QAction(const QString &text, QObject *parent = nullptr);
    void setText(const QString &text);
};

class QMenu {
public:
    QAction *addAction(const QString &text);
};

class KActionCollection {
public:
    QAction *addAction(const QString &name, const QString &text, const QObject *receiver, const char *member);
};

QString i18n(const char*);
QString i18nd(const char*, const char*);
QString ki18n(const char*);
QString ki18nd(const char*, const char*);

void test() {
    QAction *a = new QAction(i18n("Copy")); // bad
    a->setText(i18n("Paste")); // bad

    QMenu *m = new QMenu();
    m->addAction(i18n("Cut")); // bad

    KActionCollection *coll = new KActionCollection();
    coll->addAction("name", i18n("Undo"), nullptr, nullptr); // bad

    QAction *b = new QAction(ki18n("Copy")); // bad
    b->setText(i18nd("domain", "Paste")); // bad

    QMenu *m2 = new QMenu();
    m2->addAction(ki18nd("domain", "Cut")); // bad
}
