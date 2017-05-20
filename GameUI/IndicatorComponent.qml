import QtQuick 2.4

Column{
    id: iCardsLeft
    width: parent.width/3; height: parent.height
    spacing: height*0.1
    y: parent.height*0.1

    property int txt
    property string img

    Image{
        anchors.horizontalCenter: parent.horizontalCenter
        width: height; height: parent.height*0.4
        source: "../images/rooms/icons/"+ parent.img+".png"
    }

    Text{
        anchors.horizontalCenter: parent.horizontalCenter
        font {bold: true; family: fontFace.name; pixelSize: parent.height*0.3}
        color: "white"
        text: parent.txt
    }
}
