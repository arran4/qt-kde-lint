struct QString {
    QString arg(const QString&) const;
    QString toHtmlEscaped() const;
    QString() {}
    QString(const char*) {}
};
#define QStringLiteral(str) QString(str)

struct QLabel {
    void setText(const QString&);
};
struct QWidget {};
struct QMessageBox {
    static void warning(QWidget*, const QString&, const QString&);
    static void information(QWidget*, const QString&, const QString&);
};

void f() {
    QLabel* label = new QLabel;
    QString dynamicVal;

    // Pattern 2: HTML string literals built with .arg(dynamicExpr)
    label->setText(QStringLiteral("<b>%1</b>").arg(dynamicVal.toHtmlEscaped()));

    QWidget* w = nullptr;
    QMessageBox::information(w, "Title", "Static");
    QMessageBox::warning(w, "Title", dynamicVal.toHtmlEscaped());
    QMessageBox::warning(w, "Title", QString("Static"));
}
