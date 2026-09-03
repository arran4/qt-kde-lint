import QtQuick

Item {
    id: root

    function doSomething() {
        // This is a plain JavaScript object, not a QML Component
        const factory = {
            createObject: function(parent, props) {
                return props;
            }
        };

        const foundLink = "https://example.com"
        // This should not trigger the linter
        const record = factory.createObject(parent, {
            id: "record",
            url: foundLink,
        });
    }
}
