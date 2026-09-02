import QtQuick

Item {
    Component { id: comp; Rectangle {} }

    function test1() {
        comp.createObject(parent, { callback: foo(bar) }).open();
    }
}
