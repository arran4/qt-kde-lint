import QtQuick

Item {
    Component { id: comp; Rectangle {} }

    function test() {
        const menu = comp.createObject(parent);
        menu.popup();
    }
}
