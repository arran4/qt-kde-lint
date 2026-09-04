import QtQuick

Item {
    Component { id: popupComponent; Rectangle {} }

    MouseArea {
        onClicked: {
            let p = popupComponent.createObject(parent);
            if (p) p.destroy();
        }

        onTapped: {
            var n = popupComponent.createObject(parent);
            if (n) n.closed.connect(n.destroy);
        }

        onTriggered: {
            var o = popupComponent.createObject(parent);
            myArray.push(o);
        }

        onReleased: {
            var m = popupComponent.createObject(parent);
            myProp = m;
        }
    }
}
