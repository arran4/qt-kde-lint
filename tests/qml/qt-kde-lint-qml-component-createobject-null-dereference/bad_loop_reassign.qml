import QtQuick

Item {
    Component { id: comp; Rectangle {} }

    function test(shouldReplace) {
        var menu = comp.createObject(parent);
        while (shouldReplace) {
            menu = fallback;
        }
        menu.popup();
    }
}
