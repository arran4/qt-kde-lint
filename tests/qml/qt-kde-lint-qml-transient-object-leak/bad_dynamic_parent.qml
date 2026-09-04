import QtQuick

Item {
    Component { id: popupComponent; Rectangle {} }

    MouseArea {
        onTapped: {
            let dyn = getDynamicParent();
            let p = popupComponent.createObject(dyn);
            // [custom-qt-kde-lint-qml-transient-object-leak]
        }
    }
}
