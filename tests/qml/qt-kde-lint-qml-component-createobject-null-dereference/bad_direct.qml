import QtQuick

Item {
    Component { id: comp; Rectangle {} }

    function test() {
        comp.createObject(parent).open();
    }
}
