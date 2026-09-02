import QtQuick

Item {
    function test1() {
        const factory = getFactory();
        const menu = factory.createObject(parent);
        menu.popup();
    }
}
