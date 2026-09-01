struct QModelIndex {
    int row() const;
};

struct QAbstractItemModel {
    void* item(int row);
};

struct QSortFilterProxyModel : QAbstractItemModel {
    QModelIndex mapToSource(const QModelIndex& proxyIndex) const;
};

struct QAbstractItemView {
    QModelIndex currentIndex() const;
    QAbstractItemModel* model() const;
};

void testGood() {
    QAbstractItemView* view = nullptr;
    QSortFilterProxyModel* proxyModel = nullptr;
    QAbstractItemModel* sourceModel = nullptr;

    const QModelIndex proxyIndex = view->currentIndex();
    const QModelIndex sourceIndex = proxyModel->mapToSource(proxyIndex);
    auto item = sourceModel->item(sourceIndex.row());
}
