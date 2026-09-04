import QtQuick

Item {
    Component { id: popupComponent; Rectangle {} }

    Component.onCompleted: {
        let p = popupComponent.createObject(parent);
        // Not a repeatable handler
    }
}
