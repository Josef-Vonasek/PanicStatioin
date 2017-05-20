import QtQuick 2.4

Item{
    id: myItem
    width: playersHolder.width*0.3
    height: playersHolder.height* 0.5
    clip: true

    property alias name: jmeno.text
    property bool active

    state: (active ? "active" : "default")
    states: [
        State{
            name: "default"
            PropertyChanges {target: image; source: "../images/avatars/player" + index + "n.png"}
        },
        State{
            name: "active"
            PropertyChanges {target: image; source: "../images/avatars/player" + index + ".png"}
        }

    ]
    Image{
        id: image
        width: parent.width * 0.8; height: parent.height * 0.9
        source: "../images/avatars/player" + index + "n.png"
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
    }

    Rectangle{
        id: txholder

        visible: false

        anchors.top: image.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        border.width: 1
        radius: 8
        border.color: "#2c3b0d"
        width: parent.width/2
        height: width * 0.3
        color: "#999999"


        Text{
            id: jmeno
            anchors.centerIn: parent
            text: "Empty"

        }
    }
}

