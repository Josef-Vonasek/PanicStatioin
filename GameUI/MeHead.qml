import QtQuick 2.0

Rectangle{
    id: myRect
    property int human

    visible: app.hitpoints[app.me][human]

    anchors.horizontalCenter: parent.horizontalCenter
    width: parent.width*0.8; height: parent.height*0.35
    color: app._colors[me.avatar]
    radius: 5
    border {width: 5; color: Qt.lighter("grey")}

    state: {if(app.human === human){return "selected"} else {return "default"}}
    states:[
        State{
            name: "default"
            PropertyChanges{target: myRect; width: parent.width*0.7; height: parent.height*0.35}
        },
        State{
            name: "selected"
            PropertyChanges{target: myRect; width: parent.width; height: parent.height*0.48}
        }
    ]

    Behavior on height {
        PropertyAnimation {
            easing.type: Easing.OutElastic;
            easing.amplitude: 1.0;
            easing.period: 3.0;
            target: myRect;
            property: "height";
            duration: 600
        }
    }
    Behavior on width {
        PropertyAnimation {
            easing.type: Easing.OutElastic;
            easing.amplitude: 1.0;
            easing.period: 3.0;
            target: myRect;
            property: "width";
            duration: 600
        }
    }

    Image {
        width: parent.width*0.8; height: parent.height*0.8
        source: {
            if(parent.human){"../images/avatars/heads/player"+me.avatar+".png"}
            else{"../images/avatars/heads/clone"+me.avatar+".png"}
        }
        anchors.centerIn: parent
    }
    MouseArea{
        anchors.fill: parent
        onClicked:{
            app.human= myRect.human
        }
    }
}

