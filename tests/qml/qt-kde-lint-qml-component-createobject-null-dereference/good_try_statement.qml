import QtQuick

Item {
    Component { id: comp; Rectangle {} }

    function test() {
        var menu = comp.createObject(parent);
        try {
            menu = fallback;
        } finally {}
        menu.popup();
    }
}
