import QtQuick 2.0

Rectangle {
    id: myRect

    property string src
    property bool show
    signal choosed()

    width: parent.width*0.35; height: width
    radius: 6
    color: "#646464"
    border.width: 4; border.color: "white"

    Image {
        source: if(myRect.src){"../images/rooms/icons/"+myRect.src+".png"} else{""}
        anchors.centerIn: parent
        width: parent.width*0.65; height: width
        opacity: 0.4
        visible: myRect.show
    }

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onEntered: {
            focusAction.x = myRect.x;
            focusAction.y = myRect.y;
            if (myRect.show){
                focusAction.imageSrc= myRect.src
            }
            else{focusAction.imageSrc= ""}

        }
        onClicked: if(myRect.show){myRect.choosed()}

    }
}
