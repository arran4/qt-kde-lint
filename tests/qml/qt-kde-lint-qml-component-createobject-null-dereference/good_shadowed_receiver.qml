import QtQuick

Item {
    Component { id: comp; Rectangle {} }

    function test() {
        const comp = getOtherFactory();
        comp.createObject(parent).open();
    }
}
