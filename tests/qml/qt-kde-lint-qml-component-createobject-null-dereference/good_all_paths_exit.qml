import QtQuick

Item {
    Component { id: comp; Rectangle {} }

    function test(useFallback) {
        var menu = comp.createObject(parent);
        if (useFallback) {
            menu = fallback;
        } else {
            return;
        }
        menu.popup();
    }
}
