pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Basic as C

Rectangle {
    id: card
    objectName: "accessCard"
    property real unit: 1
    property string displayName: ""
    property string username: ""
    property bool allowUserSwitch: false
    property bool editingUser: false
    property bool busy: false
    property bool capsLock: false
    property string errorMessage: ""
    property string infoMessage: ""
    property string caption: "SESSÃO BLOQUEADA"
    property color accent: "#b8a1e3"
    property color ink: "#e0e3f0"
    property color muted: "#a5acc6"
    property color surface: "#11131e"
    property string fontFamily: "Adwaita Sans"
    property alias passwordText: password.text
    property alias usernameText: usernameInput.text
    property alias passwordField: password
    signal submitted()
    signal canceled()
    function focusPassword() { password.forceActiveFocus(); }
    onBusyChanged: if (!busy && visible) Qt.callLater(card.focusPassword)

    width: 392 * unit
    height: content.implicitHeight + 64 * unit
    radius: 28 * unit
    color: Qt.alpha(surface, 0.94)
    border.color: Qt.alpha(accent, 0.24)
    border.width: 1

    ColumnLayout {
        id: content
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 32 * card.unit
        spacing: 12 * card.unit

        Text {
            text: card.caption
            color: card.muted
            font.family: card.fontFamily
            font.pixelSize: 9 * card.unit
            font.letterSpacing: 2.2 * card.unit
            Layout.alignment: Qt.AlignHCenter
            Layout.bottomMargin: 8 * card.unit
        }
        Rectangle {
            implicitWidth: 72 * card.unit
            implicitHeight: implicitWidth
            Layout.alignment: Qt.AlignHCenter
            radius: width / 2
            color: Qt.alpha(card.accent, 0.12)
            border.color: Qt.alpha(card.accent, 0.35)
            Rectangle {
                anchors.fill: parent
                anchors.margins: 5 * card.unit
                radius: width / 2
                color: Qt.alpha(card.accent, 0.08)
            }
            Text {
                anchors.centerIn: parent
                text: (card.displayName || card.usernameText || "U").charAt(0).toUpperCase()
                color: card.accent
                font.family: card.fontFamily
                font.pixelSize: 29 * card.unit
                font.weight: Font.Light
            }
            Rectangle {
                width: 9 * card.unit; height: width; radius: width / 2
                anchors.right: parent.right; anchors.bottom: parent.bottom
                anchors.margins: 4 * card.unit
                color: card.accent
                border.width: 2 * card.unit; border.color: card.surface
            }
        }
        Text {
            text: card.displayName || card.usernameText || "Boas-vindas"
            color: card.ink
            font.family: card.fontFamily
            font.pixelSize: 23 * card.unit
            font.weight: Font.Medium
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
        }
        Text {
            text: card.busy ? "Verificando…" : "Bom te ver de novo."
            color: card.muted
            font.family: card.fontFamily
            font.pixelSize: 12 * card.unit
            Layout.alignment: Qt.AlignHCenter
            Layout.bottomMargin: 12 * card.unit
        }
        C.TextField {
            id: usernameInput
            objectName: "loginUsername"
            text: card.username
            visible: card.allowUserSwitch && card.editingUser
            enabled: !card.busy
            Layout.fillWidth: true
            Layout.preferredHeight: 46 * card.unit
            color: card.ink
            placeholderText: "Seu usuário"
            placeholderTextColor: card.muted
            leftPadding: 18 * card.unit
            font.family: card.fontFamily
            font.pixelSize: 14 * card.unit
            selectionColor: Qt.alpha(card.accent, 0.25)
            selectedTextColor: card.ink
            selectByMouse: true
            inputMethodHints: Qt.ImhNoAutoUppercase | Qt.ImhNoPredictiveText
            Accessible.name: "Usuário"
            background: Rectangle {
                radius: height / 2; color: Qt.alpha(card.accent, 0.045)
                border.color: usernameInput.activeFocus ? Qt.alpha(card.accent, 0.7) : Qt.alpha(card.accent, 0.18)
            }
            onAccepted: card.focusPassword()
            KeyNavigation.tab: password
        }
        RowLayout {
            Layout.fillWidth: true
            spacing: 10 * card.unit
            C.TextField {
                id: password
                objectName: "loginPassword"
                Layout.fillWidth: true
                Layout.preferredHeight: 48 * card.unit
                enabled: !card.busy
                placeholderText: "Sua senha"
                placeholderTextColor: card.muted
                echoMode: reveal.checked ? TextInput.Normal : TextInput.Password
                passwordMaskDelay: 0
                passwordCharacter: "●"
                color: card.ink
                selectionColor: Qt.alpha(card.accent, 0.25)
                selectedTextColor: card.ink
                selectByMouse: true
                leftPadding: 18 * card.unit
                rightPadding: 42 * card.unit
                font.family: card.fontFamily
                font.pixelSize: 14 * card.unit
                inputMethodHints: Qt.ImhSensitiveData | Qt.ImhNoPredictiveText | Qt.ImhNoAutoUppercase
                Accessible.name: "Senha"
                background: Rectangle {
                    radius: height / 2
                    color: Qt.alpha(card.accent, 0.045)
                    border.color: password.activeFocus ? Qt.alpha(card.accent, 0.7) : Qt.alpha(card.accent, 0.18)
                }
                onAccepted: if (!card.busy) card.submitted()
                Keys.onEscapePressed: card.canceled()
                KeyNavigation.tab: reveal
                C.Button {
                    id: reveal
                    objectName: "passwordReveal"
                    width: 36 * card.unit; height: parent.height
                    anchors.right: parent.right; anchors.rightMargin: 6 * card.unit
                    checkable: true
                    Accessible.name: checked ? "Ocultar senha" : "Mostrar senha"
                    contentItem: Canvas {
                        onPaint: {
                            var ctx = getContext("2d"); ctx.reset();
                            ctx.strokeStyle = card.muted; ctx.lineWidth = 1.2 * card.unit;
                            var x = width / 2, y = height / 2, u = card.unit;
                            ctx.beginPath(); ctx.moveTo(x - 7*u, y);
                            ctx.quadraticCurveTo(x, y - 9*u, x + 7*u, y);
                            ctx.quadraticCurveTo(x, y + 9*u, x - 7*u, y); ctx.stroke();
                            ctx.beginPath(); ctx.arc(x, y, 2*u, 0, Math.PI*2); ctx.stroke();
                        }
                    }
                    background: Rectangle { color: "transparent"; radius: height/2; border.color: reveal.activeFocus ? card.accent : "transparent" }
                    KeyNavigation.tab: submit
                }
            }
            C.Button {
                id: submit
                objectName: "loginSubmit"
                Layout.preferredWidth: 48 * card.unit
                Layout.preferredHeight: 48 * card.unit
                enabled: !card.busy
                Accessible.name: "Entrar"
                onClicked: card.submitted()
                background: Rectangle {
                    radius: width / 2
                    color: submit.hovered ? "#cbb9ed" : card.accent
                    opacity: submit.enabled ? 1 : 0.65
                    border.color: submit.activeFocus ? card.ink : "transparent"
                    border.width: 2
                }
                contentItem: Text {
                    text: card.busy ? "·" : "→"
                    color: "#20192f"
                    font.family: card.fontFamily
                    font.pixelSize: 25 * card.unit
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                KeyNavigation.tab: usernameInput.visible ? usernameInput : password
            }
        }
        Text {
            text: card.errorMessage || (card.capsLock ? "Caps Lock ativado" : card.infoMessage)
            visible: text.length > 0
            color: card.errorMessage ? "#ef9aab" : card.muted
            font.family: card.fontFamily
            font.pixelSize: 11 * card.unit
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            Accessible.role: Accessible.AlertMessage
        }
        C.Button {
            id: switchUser
            objectName: "switchUser"
            visible: card.allowUserSwitch
            enabled: !card.busy
            Layout.alignment: Qt.AlignHCenter
            topPadding: 4 * card.unit; bottomPadding: 0
            text: card.editingUser ? "Voltar" : "Trocar usuário"
            onClicked: {
                card.editingUser = !card.editingUser;
                password.clear();
                if (card.editingUser) usernameInput.forceActiveFocus();
                else card.focusPassword();
            }
            contentItem: Text { text: switchUser.text; color: switchUser.hovered ? card.ink : card.muted; font.family: card.fontFamily; font.pixelSize: 11 * card.unit }
            background: Rectangle { color: "transparent"; radius: 4; border.color: switchUser.activeFocus ? card.accent : "transparent" }
        }
    }
    Component.onCompleted: {
        if (!visible) return;
        if (card.allowUserSwitch && card.username.length === 0) {
            card.editingUser = true;
            usernameInput.forceActiveFocus();
        } else card.focusPassword();
    }
}
