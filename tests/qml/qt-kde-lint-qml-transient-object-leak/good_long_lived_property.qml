import QtQuick

Item {
    Component { id: popupComponent; Rectangle {} }
    property var myProp

    MouseArea {
        onClicked: {
            let p = popupComponent.createObject(parent);
            myProp = p;
        }
    }
}
