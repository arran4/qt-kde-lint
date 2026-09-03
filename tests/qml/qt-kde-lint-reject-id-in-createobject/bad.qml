import QtQuick

Item {
    id: root

    Component {
        id: linkMenuComponent
        Item {}
    }

    Component.onCompleted: {
        const foundLink = "https://example.com"
        const menu = linkMenuComponent.createObject(parent, {
            id: "linkMenu",
            url: foundLink,
        });
    }
}
