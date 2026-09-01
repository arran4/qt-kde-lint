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
QString i18nc(const char*, const char*);
QString i18ndc(const char*, const char*, const char*);
QString ki18nc(const char*, const char*);
QString ki18ndc(const char*, const char*, const char*);

void test() {
    QAction *a = new QAction(i18nc("@action", "Copy")); // good
    a->setText(i18nc("@action", "Paste")); // good

    QMenu *m = new QMenu();
    m->addAction(i18nc("@action:inmenu", "Cut")); // good

    KActionCollection *coll = new KActionCollection();
    coll->addAction("name", i18nc("@action", "Undo"), nullptr, nullptr); // good

    QAction *b = new QAction(ki18nc("@action", "Copy")); // good
    b->setText(i18ndc("domain", "@action", "Paste")); // good

    QMenu *m2 = new QMenu();
    m2->addAction(ki18ndc("domain", "@action:inmenu", "Cut")); // good

    // Unrelated use of i18n should not trigger
    QString s = i18n("Normal text");
}
