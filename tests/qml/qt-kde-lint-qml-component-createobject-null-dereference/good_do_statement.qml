import QtQuick

Item {
    Component { id: comp; Rectangle {} }

    function test(shouldReplace) {
        var menu = comp.createObject(parent);
        do {
            menu = fallback;
        } while (shouldReplace);
        menu.popup();
    }
}
