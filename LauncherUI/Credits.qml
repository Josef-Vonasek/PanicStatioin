import QtQuick 2.0

Item{
    id: root
    width: 800; height: 600
    anchors.centerIn: parent

    visible: false

    Image{
        anchors.fill: parent
        source: "../images/useful/bloody_wall_texture_by_Eliotchan.jpg"
    }
    MouseArea{
        anchors.fill: parent
    }

    Rectangle {
        color: "#19000000"
        anchors.fill: parent

        ListView {
            id: creditView
            width: parent.width * 0.8; height: parent.height * 0.65
            anchors.horizontalCenter: parent.horizontalCenter
            y: parent.width * 0.15
            spacing: 10
            delegate: credit
            model: ListModel{ id: creditModel
                ListElement{
                    name: "The original board game, images and rules!"
                    linkHref: "http://www.whitegoblingames.com/game/72/Panic-Station"
                    linkName: "White goblin games"
                }
                ListElement{
                    name: "Icons used in actions menu"
                    linkHref: "http://icons8.com/"
                    linkName: "Icons8"
                }
                ListElement{
                    name: "Music in game"
                    linkHref: "http://www.purple-planet.com/horror/4583971268"
                    linkName: "Purple Planet"
                }
                ListElement{
                    name: "Sound effects"
                    linkHref: "http://www.freesound.org"
                    linkName: "freesound"
                }
                ListElement{
                    name: "Photoshop brush"
                    linkHref: "http://redheadstock.deviantart.com/art/Tech-Brushes-55089850"
                    linkName: "Tech brushes"
                }
                ListElement{
                    name: "Font used in game"
                    linkHref: "http://www.dafont.com/face-your-fears.font"
                    linkName: "Face your Fears!"
                }

            }
        }
        Component{
            id: credit
            Rectangle{
                width: creditView.width; height: 60
                color: (myMouse.containsMouse ?  Qt.rgba(0, 0, 0, 0.4) : Qt.rgba(255, 255, 255, 0.1))
                border {width: 2; color: "black"}
                radius: height * 0.05
                Text{
                    x: parent.width * 0.05
                    width: parent.width *0.45; height: parent.height
                    text: name
                    verticalAlignment: Text.AlignVCenter
                    wrapMode: Text.WordWrap
                    font {bold: true; family: fontFace.name; pixelSize: parent.height * 0.2}
                    color: (myMouse.containsMouse ? "grey" : "white")
                }
                Text{
                    x: parent.width * 0.55
                    width: parent.width *0.45; height: parent.height
                    text: linkName
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    wrapMode: Text.WordWrap
                    font {italic: true; bold: true; family: fontFace.name; pixelSize: parent.height * 0.2; underline: true}
                    color: (myMouse.containsMouse ? "grey" : "white")
                }
                MouseArea{
                    id: myMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: Qt.openUrlExternally(linkHref)
                }
            }
        }

        Button {
            id: button1
            x: 1183
            y: 8
            text: "Back"
            anchors.horizontalCenterOffset: 285
            onClicked: root.visible= false
        }
    }
}
