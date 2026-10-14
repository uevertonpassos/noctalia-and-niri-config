import QtQuick

Item {
    id: header
    property color accent: "#39ff14"
    property color muted: "#8cad94"
    property string fontFamily: "MesloLGS Nerd Font"
    property string localeName: "pt_BR"
    property date currentTime: new Date()
    readonly property real unit: Math.min(1.15, Math.max(0.66, height / 1080))

    Timer {
        interval: 1000
        running: header.visible
        repeat: true
        onTriggered: header.currentTime = new Date()
    }

    Row {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: 56 * header.unit
        spacing: 12 * header.unit
        Rectangle {
            width: 6 * header.unit
            height: width
            radius: width / 2
            color: header.accent
            anchors.verticalCenter: parent.verticalCenter
        }
        Text {
            text: "[ SESSÃO BLOQUEADA ]"
            color: header.accent
            font.family: header.fontFamily
            font.pixelSize: 12 * header.unit
            font.letterSpacing: 1.5 * header.unit
        }
    }

    Column {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 56 * header.unit
        spacing: 8 * header.unit
        Text {
            anchors.right: parent.right
            text: Qt.formatDateTime(header.currentTime, "HH:mm")
            color: header.accent
            font.family: header.fontFamily
            font.pixelSize: 80 * header.unit
            font.weight: Font.Normal
        }
        Text {
            anchors.right: parent.right
            text: header.currentTime.toLocaleDateString(Qt.locale(header.localeName), "dddd, d MMMM")
            color: header.muted
            font.family: header.fontFamily
            font.pixelSize: 13 * header.unit
        }
    }
}
