import QtQuick

Item {
    Component { id: comp; Rectangle {} }

    function test(useA) {
        var menu = comp.createObject(parent);
        if (useA) {
            menu = fallbackA;
        } else {
            menu = fallbackB;
        }
        menu.popup();
    }
}
