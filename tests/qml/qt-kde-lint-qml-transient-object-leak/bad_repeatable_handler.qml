import QtQuick

Item {
    Component { id: popupComponent; Rectangle {} }

    MouseArea {
        onClicked: {
            let p = popupComponent.createObject(parent);
            // [custom-qt-kde-lint-qml-transient-object-leak]
        }
    }
}
