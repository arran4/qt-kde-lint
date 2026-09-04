import QtQuick

Item {
    Component { id: popupComponent; Rectangle {} }

    MouseArea {
        onClicked: {
            let p = popupComponent.createObject(parent);
            console.log(p);
            // [custom-qt-kde-lint-qml-transient-object-leak]
        }
    }
}
