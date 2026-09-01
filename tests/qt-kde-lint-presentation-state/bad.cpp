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
struct QAbstractButton {
    QString text() const;
};
struct QStandardItem {
    QString text() const;
};
struct QTreeWidgetItem {
    QString text() const;
};

void test() {
    QLabel label;
    if (label.text() == QStringLiteral("generating")) {} // bad

    QWidget widget;
    if (widget.windowTitle().contains(QStringLiteral("Models"))) {} // bad

    QAbstractButton *btn;
    if (btn->text() == QStringLiteral("Regenerate")) {} // bad

    QStandardItem item;
    if (item.text() == QStringLiteral("text")) {} // bad

    QTreeWidgetItem twi;
    if (twi.text() == QStringLiteral("text")) {} // bad
}
