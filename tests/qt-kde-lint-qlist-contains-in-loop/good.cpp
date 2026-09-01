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

void test_good_qset_insert(QList<QModelIndex> indexes) {
    QSet<int> rows;
    for (const QModelIndex &index : indexes) {
        rows.insert(index.row());
    }
}

void test_good_different_lists() {
    QList<int> a;
    QList<int> b;
    for (int i = 0; i < 10; ++i) {
        if (!a.contains(i)) {
            b.append(i);
        }
    }
}

void test_good_no_loop() {
    QList<int> rows;
    if (!rows.contains(1)) {
        rows.append(1);
    }
}

void test_good_just_contains() {
    QList<int> rows;
    for (int i = 0; i < 10; ++i) {
        if (!rows.contains(i)) {
            // do nothing
        }
    }
}

struct TestFieldGood {
    QList<int> a;
    QList<int> b;
    void test_good_different_fields() {
        for (int i = 0; i < 10; ++i) {
            if (!a.contains(i)) {
                b.append(i);
            }
        }
    }
};

struct TestMix {
    QList<int> a;
    void test_good_mix() {
        QList<int> b;
        for (int i = 0; i < 10; ++i) {
            if (!a.contains(i)) {
                b.append(i);
            }
        }
    }
};

struct TestMix2 {
    QList<int> a;
    void test_good_mix2() {
        QList<int> b;
        for (int i = 0; i < 10; ++i) {
            if (!b.contains(i)) {
                a.append(i);
            }
        }
    }
};
