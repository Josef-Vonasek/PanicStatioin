import QtQuick 2.0

Rectangle {
    id: myRect
    width: 150
    height: 60
    radius: 10
    anchors.horizontalCenter: parent.horizontalCenter
    gradient: Gradient {
        GradientStop {
            position: 0
            color: "#80b6b6b6"
        }

        GradientStop {
            position: 1
            color: "#cc424242"
        }
    }
    border.width: 4
    border.color: (myMouse.containsMouse ? "white" : "black")


    property string text

    signal clicked

    Text{
        anchors.fill: parent
        font {bold: true; pixelSize: parent.height * 0.3; family: fontFace.name}
        color: (myMouse.containsMouse ? "white" : "black")
        text: myRect.text
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        wrapMode: Text.WordWrap
    }
    MouseArea{
        id: myMouse
        anchors.fill: parent
        hoverEnabled: true
        onEntered: app._hoverButton()
        onClicked: {app._clickButton(); parent.clicked()}
    }
}

