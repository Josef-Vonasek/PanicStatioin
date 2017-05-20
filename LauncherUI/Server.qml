import QtQuick 2.4

Rectangle {
    id: root
    width: 800; height: 600
    color: "#19000000"


    signal renameServer(string name)
    onRenameServer: nameInput.text = name

    signal newVolume(double voip, double music, double effects)
    onNewVolume: {
        setVolume.voip = voip
        setVolume.music = music
        setVolume.effects = effects
    }

    property bool admin: (app.me === 0)

    Rectangle {
        id: rectangle1
        x: 8
        y: 77
        width: 624
        height: 515
        color: "#19000000"
        radius: 20
        border.width: 4

        Item{
            id: playersHolder
            anchors.centerIn: parent
            width: parent.width; height: parent.height *0.9
            clip: true

            Grid{
                id: players
                columns: 3
                spacing: playersHolder.width*0.01
                anchors.centerIn: parent

                Repeater{
                    id: repeater
                    model: 6

                    delegate: PlayerItem{
                        active: app.players[index]
                        name: app.names[index]
                    }
                }
            }
        }
    }

    Column {
        id: buttonColumn
        x: 638
        y: 77
        width: 154
        height: 300
        spacing: 10

        Button {
            visible: root.admin
            text: "Start"
            onClicked: app._start()
        }

        Button {
            text: "Disconnect"
            onClicked: app._disconnect()

        }
    }


    Column {
        id: column2
        x: 638
        y: 453
        width: 154
        height: 129

        spacing: 10

        Button {
            text: "Credits!"
            onClicked: credits.visible= true
        }

        Button {
            id: button4
            text: "QUIT"
            onClicked: app._quit()
        }
    }

    Rectangle {
        id: rectangle2
        x: 29
        y: 11
        width: 448
        height: 60
        color: "#80000000"
        radius: 5
        border.color: "#000000"
        border.width: 2

        TextInput {
            id: nameInput
            anchors{verticalCenter: parent.verticalCenter; left: nameText.right}
            width: parent.width *0.7; height: parent.height * 0.6
            color: "#731e1e"
            text: qsTr("EnderovaHra")
            selectionColor: "#f24040"
            horizontalAlignment: Text.AlignLeft
            clip: false
            font {family: fontFace.name; bold: true; pixelSize: height * 0.8}
            maximumLength: 15
            readOnly: !root.admin

            onAccepted: {app.write= [text];app.serverName = text}
        }

        Text {
            id: nameText
            anchors.verticalCenter: parent.verticalCenter
            x: parent.width* 0.05
            width: parent.width * 0.21
            height: parent.height * 0.6
            color: "#731e1e"
            text: qsTr("Name:  ")
            styleColor: "#000000"
            font {family: fontFace.name; bold: true; pixelSize: height * 0.8}
        }
    }

    Image {
        id: image1
        x: 721
        y: 11
        width: 60
        height: 60
        source: "../images/rooms/icons/settingsico.png"

        MouseArea{
            anchors.fill: parent
            onClicked: (setVolume.visible ? setVolume.visible = false : setVolume.visible = true)
        }
    }

    Volume {
        id: setVolume
    }
    Credits{
        id: credits
    }
}

