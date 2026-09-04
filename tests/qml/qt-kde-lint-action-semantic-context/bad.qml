import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    Action {
        // [custom-qt-kde-lint-action-semantic-context]
        text: i18n("Copy Link Address")
    }

    Action {
        id: customAction
        // [custom-qt-kde-lint-action-semantic-context]
        text: i18nd("mydomain", "Copy Link Address")
    }

    Kirigami.Action {
        // [custom-qt-kde-lint-action-semantic-context]
        text: i18n("Do Something")
    }
}
