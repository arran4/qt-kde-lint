import QtQuick

Item {
    id: rootItem
    property var saved
    Component { id: popupComponent; Rectangle {} }

    MouseArea {
        onClicked: {
            let p = popupComponent.createObject(parent)
            rootItem.saved = p
        }
    }
}
