import QtQuick

Item {
    Component { id: comp; Rectangle {} }

    function test() {
        var menu = comp.createObject(parent);
        menu = null; // Unrelated assignment
        menu.popup(); // We shouldn't flag this under this specific rule anymore since it was reassigned
    }
}
