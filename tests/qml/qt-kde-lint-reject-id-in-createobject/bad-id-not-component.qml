import QtQuick

Item {
    id: root

    Component {
        id: maker
        Item {}
    }

    Component.onCompleted: {
        maker.createObject(parent, { id: "bad" });
    }
}
