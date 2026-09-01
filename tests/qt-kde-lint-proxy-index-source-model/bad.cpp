struct QModelIndex {
    int row() const;
};

struct QAbstractItemModel {
    void* item(int row);
};

struct QSortFilterProxyModel : QAbstractItemModel {
};

struct QAbstractItemView {
    QModelIndex currentIndex() const;
    QAbstractItemModel* model() const;
};

void testBad() {
    QAbstractItemView* view = nullptr;
    QAbstractItemModel* sourceModel = nullptr;

    const QModelIndex index = view->currentIndex();
    auto item = sourceModel->item(index.row());
}
