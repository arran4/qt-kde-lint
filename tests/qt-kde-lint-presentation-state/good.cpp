struct QString {
    bool operator==(const QString&) const;
    bool contains(const QString&) const;
};
struct QStringLiteral {
    QStringLiteral(const char*);
    operator QString() const;
};
struct QWidget {
    QString windowTitle() const;
};
struct QLabel {
    QString text() const;
};
void test() {
    QString state = QStringLiteral("generating");
    if (state == QStringLiteral("generating")) {} // good
}
