import QtQuick

Item {
    Component { id: comp; Rectangle {} }

    function test() {
        var menu = comp.createObject(parent);
        if (menu === null && shouldReturn) return;
        menu.popup();
    }
}
