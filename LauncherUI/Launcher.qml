import QtQuick 2.4
import ParanoiaLauncher 1.0

App{
    id: app
    width: 800; height: 600

    Component.onCompleted: _completed()

    signal connected
    onConnected: state = "Server"

    signal disconnected
    onDisconnected: state = "Search"


    signal addServer(int i, string ip, string name, string players, string active)
    onAddServer: loader.item.addServer(i, ip, name, players, active)

    signal removeServer(int i)
    onRemoveServer: loader.item.removeServer(i)

    signal renameServer(string name)
    onRenameServer: loader.item.renameServer(name)

    signal setVolume(double voip, double music, double effects)
    onSetVolume: loader.item.newVolume(voip, music, effects)

    state: "Search"
    states: [
        State{
            name: "Search"
            PropertyChanges{target: loader; source: "Search.qml"}
        },
        State{
            name: "Server"
            PropertyChanges{target: loader; source: "Server.qml"}
        }
    ]

    Rectangle{
        anchors.fill: parent

        color: "#444444"

        Image{
            anchors.centerIn: parent
            width: 800; height: 600
            source: "../images/useful/bloody_wall_texture_by_Eliotchan.jpg"     //DeviantArt
        }

        Loader {
            id: loader
            anchors.centerIn: parent

            source: "Search.qml"
        }
    }

    FontLoader{
        id: fontFace
        source: "../Font/FaceYourFears.ttf"
    }
}
