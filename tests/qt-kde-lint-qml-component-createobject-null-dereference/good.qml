import QtQuick

Item {
    Component {
        id: comp
        Rectangle {}
    }

    function test1() {
        comp.createObject(parent)?.open();
    }

    function test2() {
        const menu = comp.createObject(parent);
        menu?.popup();
    }

    function test3() {
        const menu = comp.createObject(parent);
        if (menu) {
            menu.popup();
        }
    }
}
