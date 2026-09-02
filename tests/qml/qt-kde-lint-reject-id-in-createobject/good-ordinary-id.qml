import QtQuick

Item {
    // Normal declarative ID should not trigger the rule
    id: ordinaryIdFoo

    Component {
        id: linkMenuComponent
        Item {}
    }

    Component.onCompleted: {
        const foundLink = "https://example.com"
        const menu = linkMenuComponent.createObject(parent, {
            objectName: "linkMenu",
            url: foundLink,
        });
    }
}
