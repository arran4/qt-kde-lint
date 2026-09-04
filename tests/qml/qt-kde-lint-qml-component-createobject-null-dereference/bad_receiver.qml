import QtQuick

Item {
    Component { id: comp; Rectangle {} }

    function test() {
        // Not shadowed
        comp.createObject(parent).open();
    }
}
