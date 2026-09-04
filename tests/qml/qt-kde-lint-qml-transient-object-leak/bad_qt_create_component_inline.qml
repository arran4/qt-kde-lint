import QtQuick

Item {
    MouseArea {
        onClicked: {
            let p = Qt.createComponent("MyMenu.qml").createObject(parent);
            // [custom-qt-kde-lint-qml-transient-object-leak]
        }
    }
}
