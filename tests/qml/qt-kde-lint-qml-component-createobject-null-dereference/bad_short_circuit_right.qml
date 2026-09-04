import QtQuick

Item {
    Component { id: comp; Rectangle {} }

    function test() {
        var menu = comp.createObject(parent);
        var otherMenu = comp.createObject(parent);
        // "otherMenu.enabled" should trigger an issue because it's evaluated safely
        // but otherMenu itself is NOT verified!
        if (menu && otherMenu.enabled) {
            menu.popup();
        }
    }
}
