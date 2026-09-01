class QModelIndex {
public:
    int row() const { return 0; }
};

template <typename T>
class QList {
public:
    bool contains(const T &value) const { return false; }
    void append(const T &value) {}
    void push_back(const T &value) {}
    void operator<<(const T &value) {}
    T* begin() { return nullptr; }
    T* end() { return nullptr; }
};

template <typename T>
class QSet {
public:
    bool contains(const T &value) const { return false; }
    void insert(const T &value) {}
};

void test_bad_range_loop_append(QList<QModelIndex> indexes) {
    QList<int> rows;
    for (const QModelIndex &index : indexes) {
        if (!rows.contains(index.row())) {
            rows.append(index.row());
        }
    }
}

void test_bad_range_loop_push_back(QList<QModelIndex> indexes) {
    QList<int> rows;
    for (const QModelIndex &index : indexes) {
        if (!rows.contains(index.row())) {
            rows.push_back(index.row());
        }
    }
}

void test_bad_range_loop_operator(QList<QModelIndex> indexes) {
    QList<int> rows;
    for (const QModelIndex &index : indexes) {
        if (!rows.contains(index.row())) {
            rows << index.row();
        }
    }
}

void test_bad_range_loop_without_braces(QList<QModelIndex> indexes) {
    QList<int> rows;
    for (const QModelIndex &index : indexes) {
        if (!rows.contains(index.row()))
            rows.append(index.row());
    }
}

void test_bad_for_loop() {
    QList<int> rows;
    for (int i = 0; i < 10; ++i) {
        if (!rows.contains(i)) {
            rows.append(i);
        }
    }
}

void test_bad_while_loop() {
    QList<int> rows;
    int i = 0;
    while (i < 10) {
        if (!rows.contains(i)) {
            rows.append(i);
        }
        ++i;
    }
}

void test_bad_do_while_loop() {
    QList<int> rows;
    int i = 0;
    do {
        if (!rows.contains(i)) {
            rows.append(i);
        }
        ++i;
    } while (i < 10);
}

struct TestField {
    QList<int> rows;
    void test_bad_field_range_loop(QList<QModelIndex> indexes) {
        for (const QModelIndex &index : indexes) {
            if (!rows.contains(index.row())) {
                rows.append(index.row());
            }
        }
    }
};

struct TestThisField {
    QList<int> rows;
    void test_bad_this_field_range_loop(QList<QModelIndex> indexes) {
        for (const QModelIndex &index : indexes) {
            if (!this->rows.contains(index.row())) {
                this->rows.append(index.row());
            }
        }
    }
};

void test_bad_range_loop_operator_plus_equal(QList<QModelIndex> indexes) {
    QList<int> rows;
    for (const QModelIndex &index : indexes) {
        if (!rows.contains(index.row())) {
            rows += index.row();
        }
    }
}
