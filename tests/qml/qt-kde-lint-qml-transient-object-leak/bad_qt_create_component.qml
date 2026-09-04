import QtQuick

Item {
    MouseArea {
        onClicked: {
            let c = Qt.createComponent("MyMenu.qml");
            let p = c.createObject(parent);
            // [custom-qt-kde-lint-qml-transient-object-leak]
        }
    }
}
