import QtQuick 2.4
import QtQuick.Controls 1.2

Rectangle{
    id: rect
    anchors.centerIn: parent
    width: 400
    height: 400
    color: "#ccffffff"
    radius: 50
    border.width: 10

    visible: false

    property alias voip: voipSlider.value
    property alias music: musicSlider.value
    property alias effects: effectSlider.value

    MouseArea{
        anchors.fill: parent
    }

    Column {
        x: 40
        y: 75
        width: 320
        height: 255
        spacing: 10
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter

        Text {
            width: 167
            height: 37
            color: "#494949"
            text: qsTr("VOIP :")
            anchors.left: parent.left
            anchors.leftMargin: 0
            textFormat: Text.AutoText
            font {italic: true; bold: true; family: fontFace.name; pixelSize: 25}
            verticalAlignment: Text.AlignVCenter
        }


        Slider {
            id: voipSlider
            width: 275
            height: 27
            anchors.horizontalCenterOffset: 0
            activeFocusOnPress: true
            anchors.horizontalCenter: parent.horizontalCenter
        }


        Text {
            width: 167
            height: 37
            color: "#494949"
            text: qsTr("Music :")
            anchors.left: parent.left
            anchors.leftMargin: 0
            font {italic: true; bold: true; family: fontFace.name; pixelSize: 25}
            verticalAlignment: Text.AlignVCenter
            textFormat: Text.AutoText
        }


        Slider {
            id: musicSlider
            width: 275
            height: 32
            anchors.horizontalCenterOffset: 0
            activeFocusOnPress: true
            anchors.horizontalCenter: parent.horizontalCenter
        }



        Text {
            width: 167
            height: 37
            color: "#494949"
            text: qsTr("Effects :")
            anchors.left: parent.left
            anchors.leftMargin: 0
            font {italic: true; bold: true; family: fontFace.name; pixelSize: 25}
            verticalAlignment: Text.AlignVCenter
            textFormat: Text.AutoText
        }

        Slider {
            id: effectSlider
            width: 275
            height: 33
            anchors.horizontalCenterOffset: 0
            activeFocusOnPress: true
            stepSize: 0
            anchors.horizontalCenter: parent.horizontalCenter
        }

    }

    Text {
        x: 69
        y: 19
        width: 262
        height: 42
        color: "#141414"
        text: qsTr("Sound Volume")
        anchors.horizontalCenter: parent.horizontalCenter
        font {italic: true; family: fontFace.name; bold: true; pixelSize: 35}
        horizontalAlignment: Text.AlignHCenter
    }

    Rectangle {
        x: 153
        y: 333
        width: 100
        height: 50
        color: "#80ffffff"
        radius: 20
        border.color: "#262626"
        anchors.topMargin: 6
        border.width: 5
        anchors.horizontalCenterOffset: 0
        anchors.horizontalCenter: parent.horizontalCenter

        Text {
            color: "#262626"
            anchors.fill: parent
            text: qsTr("Apply")
            font {italic: true; bold: true; family: fontFace.name; pixelSize: 25}
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
        MouseArea{
            anchors.fill: parent
            onClicked: {
                app._changeVolume(voipSlider.value, musicSlider.value, effectSlider.value)
            }
        }
    }
}
