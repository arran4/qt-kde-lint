import QtQuick

Item {
    Component { id: popupComponent; Rectangle {} }

    MouseArea {
        onClicked: {
            if (true) {
                let p = popupComponent.createObject(parent);
                if (p) p.visible = true;
                // [custom-qt-kde-lint-qml-transient-object-leak]
            }
        }
    }
}
