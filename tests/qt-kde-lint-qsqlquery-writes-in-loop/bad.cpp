#include <vector>

class QString {
public:
    QString(const char*);
};

class QSqlDatabase {
public:
    bool transaction();
    bool commit();
};

class QSqlQuery {
public:
    QSqlQuery();
    QSqlQuery(QSqlDatabase db);
    bool prepare(const QString& query);
    bool exec();
    bool exec(const QString& query);
    bool execBatch();
};

void bad(const std::vector<int>& items, QSqlDatabase db) {
    for (const auto &item : items) {
        QSqlQuery query(db);
        query.prepare("UPDATE things SET state = 1 WHERE id = 1");
        query.exec(); // Warning
    }
}
