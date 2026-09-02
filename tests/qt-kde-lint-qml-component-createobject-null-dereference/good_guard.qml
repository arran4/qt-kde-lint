import QtQuick

Item {
    Component { id: comp; Rectangle {} }

    function test1() {
        const menu = comp.createObject(parent);
        if (menu !== null) {
            menu.popup();
        }
    }

    function test2() {
        const menu = comp.createObject(parent);
        if (menu) {
            menu.popup();
        }
    }
}
