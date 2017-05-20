import QtQuick 2.4
import QtGraphicalEffects 1.0

Item{
    id: myItem
    height: app.height * 0.2
    width: app.width *0.08
    y: {target.width*1.1 - y1 - height/2}
    x: {target.width*0.5 + x1 - width/2}

    rotation: offset * 6
    scale: 1 - 0.08* Math.abs(offset)

    property Item target
    property variant cards

    property string name
    property int number

    property double offset: (Math.PI* 0.50 - angle) * 15
    property int _radius: target.width *1

    property double angle: {
        Math.PI * 0.34 + ((Math.PI*0.32/(1 + cards.length)) * (1 + index))
    }
    property int y1: Math.sin(angle) * _radius
    property int x1: Math.cos(angle) * _radius

    Behavior on y {
        NumberAnimation {
            easing.type: Easing.OutQuad
            duration: 300
        }
    }
    Behavior on x {
        NumberAnimation {
            easing.type: Easing.OutQuad
            duration: 300
        }
    }
    Behavior on scale{
        NumberAnimation{
            easing.type: Easing.OutQuad
            duration: 500
        }
    }

    state: "default"
    states: [
        State{
            name: "default"
            PropertyChanges{target: myItem; _radius: target.width }
        },
        State{
            name: "hover"
            PropertyChanges{target: myItem; _radius: target.width * 1.05 }
        }

    ]

    MouseArea{
        anchors.fill: parent
        hoverEnabled: true
        propagateComposedEvents: true
        onClicked: {
            if(blocker._state === "pickingCard" && !pickCard.sent){pickCard.cardImg= name; pickCard.cardSet= true}
            else {app._useCard(myItem.name)}

        }
        onEntered: {
            myItem.z= 1
            myItem.scale= 1
            myItem._radius= target.width*1.05
            if(blocker._state === "pickingCard"  && !pickCard.cardSet){pickCard.cardImg= name}
            else {useMask.visible= true}
        }
        onExited: {
            myItem.z= 0
            myItem.scale= 1 - 0.08* Math.abs(offset)
            myItem._radius= Qt.binding(function(){return target.width})
            if(blocker._state === "pickingCard"  && !pickCard.cardSet){pickCard.cardImg= ""}
            else {useMask.visible= false}
        }
    }


    Image{
        id: im
        anchors.fill: parent
        source: {
            var _name
            if(myItem.name.substring(0, 4) === "blood"){_name = "blood" +  app.avatars[parseInt(myItem.name.substring(-1))]}
            else {_name = myItem.name}
            return ("../images/rooms/cards/"+_name+".png")
        }
    }
    Rectangle{
        visible: if(myItem.number > 0){true}else {false}
        height: 25
        width: 25
        radius: 13
        border.width: 2
        anchors.top: parent.top
        anchors.right: parent.right
        Text {
            anchors.centerIn: parent
            text: myItem.number
            font {bold: true; family: fontFace.name}

        }
    }

    Rectangle{
        id: greenMask
        anchors.fill: parent
        opacity: 0.5
        visible: false
        color: "green"
    }

    OpacityMask{
        id: useMask
        anchors.fill: parent
        source: greenMask
        maskSource: im
        visible: false
        opacity: 0.5

        Rectangle{
            anchors.centerIn: useMask
            width: useMask.width*0.5; height: width
            radius: width/2
            border {width: 3; color: "black"}
            color: "darkGrey"

            Text{
                anchors.centerIn: parent
                font {bold: true; family: fontFace.name; pixelSize: parent.width*0.3}
                color: "black"
                text: "USE"
            }
        }
    }
}

