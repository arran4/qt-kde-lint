import QtQuick

Item {
    id: root

    function doSomething() {
        // This is a plain JavaScript object, not a QML Component
        const factoryComponent = {
            createObject: function(parent, props) {
                return props;
            }
        };

        const foundLink = "https://example.com"
        // This should not trigger the linter even though its name contains Component
        const record = factoryComponent.createObject(parent, {
            id: "record",
            url: foundLink,
        });
    }
}
