import QtQuick

Item {
    Component { id: comp; Rectangle {} }

    function test() {
        var menu = comp.createObject(parent);
        if (menu && menu.enabled) {
            menu.popup();
        }
    }

    function test2() {
        var menu = comp.createObject(parent);
        if (menu !== null && menu.enabled) {
            menu.popup();
        }
    }
}
