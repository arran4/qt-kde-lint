import QtQuick

Item {
    Component { id: comp; Rectangle {} }

    function test() {
        var menu = comp.createObject(parent);
        if (menu.enabled && menu) {
            menu.popup();
        }
    }
}
