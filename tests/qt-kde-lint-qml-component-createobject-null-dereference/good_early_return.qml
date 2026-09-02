import QtQuick

Item {
    Component { id: comp; Rectangle {} }

    function test1() {
        const menu = comp.createObject(parent);
        if (!menu) return;
        menu.popup();
    }
}
