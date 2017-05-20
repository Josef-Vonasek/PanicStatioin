import QtQuick 2.4

Rectangle {
    id: root
    width: 800; height: 600
    color: "#19000000"

    signal addServer(int index, string ip, string name, string players, string active)
    onAddServer:{
        if (index === -1){
            serverModel.append({"_index": serverModel.count, "_name": name, "_players": players, "_ipAddress": ip, "_active": active})
        }
        else{
            serverModel.set(index, {"_index": index, "_name": name, "_players": players, "_ipAddress": ip, "_active:": active})
        }
    }

    signal removeServer(int index)
    onRemoveServer: {
        serverModel.remove(index)
    }

    signal newVolume(double voip, double music, double effects)
    onNewVolume: {
        setVolume.voip = voip
        setVolume.music = music
        setVolume.effects = effects
    }



    MouseArea{
        anchors.fill: parent
        onClicked: inputHolder.state = "default"
    }



    Rectangle {
        id: rectangle1
        x: 8
        y: 77
        width: 624
        height: 515
        color: "#19000000"
        radius: 20
        border.width: 4


        ServerInfo {
            x: 92
            y: 22

            color: Qt.rgba(255, 255, 255, 0.2)
            border.color: "black"

            index: -1
            name: "Name"
            players: "Players"
            ipAddress: "IP Address"
            active: "State"
        }

        ListView {
            id: gamesView

            x: 12
            y: 130
            width: 600
            height: 312
            clip: false
            spacing: 10

            property string selected: "IP Address"

            model: ListModel {
                id: serverModel
            }
            delegate: ServerInfo{
                index: _index
                name: _name
                players: _players
                ipAddress: _ipAddress
                active: _active
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
            text: "Create"
            onClicked: app._createServer()
        }

        Button {
            text: "Connect"
            onClicked: if(gamesView.selected !== "IP Address"){app._connectTo(gamesView.selected)}
        }

        Button {
            text: "Direct Connection"
            onClicked: inputHolder.state = "server"
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

    Item{
        id: inputHolder

        width: parent.width
        height: 80

        state: "default"
        states: [
            State{
                name: "default"
                PropertyChanges{target: inputHolder; visible: false}
            },
            State{
                name: "name"
                PropertyChanges{target: inputHolder; visible: true}
                PropertyChanges{target: nameText; text: qsTr("Name:  ")}
            },
            State{
                name: "server"
                PropertyChanges{target: inputHolder; visible: true}
                PropertyChanges{target: nameText; text: qsTr("IP:    ")}
            }
        ]


        Rectangle {
            id: inputRect
            x: 23
            y: 11
            width: 448
            height: 60
            color: "#4cffffff"
            radius: 5
            anchors.verticalCenter: parent.verticalCenter
            border.color: "#000000"
            border.width: 2

            TextInput {
                id: nameInput
                anchors{verticalCenter: parent.verticalCenter; left: nameText.right}
                width: parent.width *0.7; height: parent.height * 0.6
                color: "#112b4e"
                text: qsTr("")
                selectionColor: "#f24040"
                horizontalAlignment: Text.AlignLeft
                clip: true
                font {bold: true; family: fontFace.name; pixelSize: height * 0.8}
                maximumLength: 15

                onAccepted: inputOkay.clicked()
            }

            Text {
                id: nameText
                anchors.verticalCenter: parent.verticalCenter
                x: parent.width* 0.05
                width: parent.width * 0.21
                height: parent.height * 0.6
                color: "#000000"
                text: qsTr("Name:  ")
                font {bold: true; family: fontFace.name; pixelSize: height * 0.8}
            }
        }

        Button{
            id: inputOkay
            x: 11
            y: 11
            width: 114
            text: "Okay"
            anchors.verticalCenterOffset: 0
            anchors.horizontalCenterOffset: 174
            anchors.verticalCenter: parent.verticalCenter
            onClicked: {
                if(inputHolder.state == "name"){}
                else if(inputHolder.state == "server"){app._connectTo(nameInput.text)}
            }

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

    Credits {
        id: credits
    }

    Column {
        id: column1
        width: 200
        height: 400
    }

}

