import QtQuick

Item {
    Component { id: popupComponent; Rectangle {} }

    MouseArea {
        onClicked: {
            let holder = {}
            let p = popupComponent.createObject(parent)
            holder.value = p
            // [custom-qt-kde-lint-qml-transient-object-leak]
        }
    }
}
