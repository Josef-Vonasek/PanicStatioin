import QtQuick 2.4
import QtGraphicalEffects 1.0

Item{
    id: myItem
    width: directionPicker.width*0.25; height: width

    property variant move
    property string img: "rightArrowico"

    Rectangle{
        id: rect
        visible: false
        anchors.fill: parent
        color: {
            if (directionPicker.selected === myItem.move) {"green"}
            else if (directionPicker.hovered === myItem.move) {"white"}
            else {"grey"}
        }
    }

    Image{
        id: im
        visible: false
        anchors.centerIn: parent
        width: parent.width*0.8; height: width
        source: "../images/rooms/icons/" + myItem.img + ".png"
    }

    OpacityMask{
        anchors.fill: parent
        source: rect
        maskSource: im
    }

    MouseArea{
        anchors.fill: parent
        hoverEnabled: true
        onClicked:{
            app._newMeeting(myItem.move)
            directionPicker.selected= myItem.move
        }
        onEntered:{
            if (directionPicker.selected !== myItem.move) {directionPicker.hovered = myItem.move}
        }
        onExited: {
            if (directionPicker.selected !== myItem.move) {directionPicker.hovered = []}
        }
    }
}

