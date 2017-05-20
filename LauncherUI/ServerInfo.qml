import QtQuick 2.4
import QtQuick 2.4

Rectangle {
    width: 600
    height: 50
    color: (myMouse.containsMouse || gamesView.selected === ipAddress ?  Qt.rgba(255, 255, 255, 0.4) : Qt.rgba(255, 255, 255, 0.1))
    radius: 5
    border.width: 2
    border.color: (gamesView.selected === ipAddress ? "white" : "black")

    anchors.horizontalCenter: parent.horizontalCenter


    signal clicked

    onClicked: gamesView.selected = ipAddress

    property int index
    property string name
    property string players
    property string ipAddress
    property string active

    Text{
        x: parent.width * 0.05
        anchors.verticalCenter: parent.verticalCenter
        font {bold: true; italic: true; family: fontFace.name; pixelSize: parent.height * 0.3}
        text: name
        horizontalAlignment: Text.AlignLeft
    }
    Text{
        x: parent.width * 0.4 - width/2
        anchors.verticalCenter: parent.verticalCenter
        font {bold: true; italic: true; family: fontFace.name; pixelSize: parent.height * 0.3}
        text: players
        horizontalAlignment: Text.AlignHCenter
    }
    Text{
        x: parent.width * 0.6
        anchors.verticalCenter: parent.verticalCenter
        font {bold: true; italic: true; family: fontFace.name; pixelSize: parent.height * 0.3}
        text: ipAddress
        horizontalAlignment: Text.AlignHCenter
    }
    Text{
        x: parent.width * 0.86
        anchors.verticalCenter: parent.verticalCenter
        font {bold: true; italic: true; family: fontFace.name; pixelSize: parent.height * 0.3}
        text: active
        horizontalAlignment: Text.AlignHCenter
        color: if(active === "Waiting") {"darkGreen"} else if (active === "In Game") {"darkRed"}
    }

    MouseArea{
        id: myMouse

        anchors.fill: parent
        hoverEnabled: true
        onClicked: parent.clicked()
    }


}

