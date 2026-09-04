import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    Action {
        text: i18nc("@action", "Copy Link Address")
    }

    Kirigami.Action {
        text: i18ndc("mydomain", "@action", "Do Something")
    }

    // Ordinary text properties should not trigger
    Text {
        text: i18n("Normal text")
    }

    Label {
        text: i18n("Normal label")
    }

    // Other properties should not trigger
    Action {
        description: i18n("Action description")
        tooltip: i18n("Tooltip")
    }

    // String literals lookalikes or other forms shouldn't crash it
    Action {
        text: "i18n('Copy Link Address')"
    }

    // Custom objects should not trigger
    MyObject {
        text: i18n("Custom object text")
    }

    MyControls.Action {
        text: i18n("Custom action-like component")
    }

    Something.Action {
        text: i18nd("mydomain", "Custom action")
    }
}
