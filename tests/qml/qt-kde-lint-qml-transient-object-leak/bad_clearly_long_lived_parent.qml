import QtQuick

Item {
    id: rootItem
    Component { id: popupComponent; Rectangle {} }

    MouseArea {
        onClicked: {
            let p = popupComponent.createObject(rootItem);
            // [custom-qt-kde-lint-qml-transient-object-leak]
        }
    }
}
