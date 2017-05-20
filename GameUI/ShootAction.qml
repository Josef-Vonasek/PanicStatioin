import QtQuick 2.0

Item{
    id: myRect
    anchors.verticalCenter: parent.verticalCenter
    width: actionsView.height; height: width

    property string name
    property int parasite
    property int player1
    property int human1
    property int player2
    property int human2
    property int demage
    property string src
    property variant pList: []


    state: name
    states:[
        State{
            name: "explore"
            PropertyChanges{target: p2Rect; visible: false}
            PropertyChanges{target: a1Rect; visible: false}
            PropertyChanges{target: a2Rect; img: "../images/rooms/rooms/"+src+".png"}
        },
        State{
            name: "changingCards"
            PropertyChanges{target: a2Rect; visible: false}
            PropertyChanges{target: a1Rect; img: "../images/rooms/icons/exchangeico.png"}
        },
        State{
            name: "shoot"
            PropertyChanges{target: a2Rect; visible: false}
            PropertyChanges{target: a1Rect; img: "../images/rooms/icons/gunico.png"}
        },
        State{
            name: "stab"
            PropertyChanges{target: a2Rect; visible: false}
            PropertyChanges{target: a1Rect; img: "../images/rooms/icons/knifeico.png"}
        },
        State{
            name: "palmScan"
            PropertyChanges{target: a2Rect; visible: false}
            PropertyChanges{target: a1Rect; img: "../images/rooms/icons/palmscanico.png"}
        },
        State{
            name: "useCard"
            PropertyChanges{target: p2Rect; visible: false}
            PropertyChanges{target: a1Rect; visible: false}
            PropertyChanges{target: a2Rect; img: "../images/rooms/cards/"+src+".png"}
        },
        State{
            name: "drawCard"
            PropertyChanges{target: p2Rect; visible: false}
            PropertyChanges{target: a1Rect; visible: false}
            PropertyChanges{target: a2Rect; img: "../images/rooms/cards/back0.png"}
        },
        State{
            name: "throwGrenade"
            PropertyChanges{target: a2Rect; visible: false}
            PropertyChanges{target: p2Rect; visible: false}
            PropertyChanges{target: a1Rect; visible: false}
            PropertyChanges{target: a3Rect; visible: true; img: "../images/rooms/icons/grenadeico.png"}
        },
        State{
            name: "scan"
            PropertyChanges{target: p2Rect; visible: false}
            PropertyChanges{target: a1Rect; img: "../images/rooms/icons/fingerscanico.png"}
        },
        State{
            name: "heal"
            PropertyChanges{target: p2Rect; visible: false}
            PropertyChanges{target: a1Rect; img: "../images/rooms/icons/healico.png"}
        },
        State{
            name: "burn"
            PropertyChanges{target: p2Rect; visible: false}
            PropertyChanges{target: a1Rect; img: "../images/rooms/icons/burnico.png"}
        },
        State{
            name: "scan"
            PropertyChanges{target: p2Rect; visible: false}
            PropertyChanges{target: a1Rect; img: "../images/rooms/icons/fingerscanico.png"}
        },
        State{
            name: "openDoors"
            PropertyChanges{target: p2Rect; visible: false}
            PropertyChanges{target: a1Rect; img: "../images/rooms/icons/doorico.png"}
        },
        State{
            name: "parasiteAttack"
            PropertyChanges{target: a2Rect; visible: false}
            PropertyChanges{target: p2Rect; visible: false}
            PropertyChanges{target: a1Rect; visible: false}
        }

    ]


    Image{
        anchors.fill: parent
        source: "../images/useful/ActionFrame.png"
    }

    Rectangle{
        id: holder
        width: parent.width*0.6; height: parent.height*0.58
        x: parent.width*0.2; y: parent.height*0.18
        color: "#00000000"
        border.width: 0

        property int avatar1: app.avatars[myRect.player1]
        property int avatar2: app.avatars[myRect.player2]


        Rectangle{
            id: p1Rect
            anchors {top: parent.top; left: parent.left}
            width: parent.width*0.4; height: width
            border {width: 2; color: "black"}
            radius: width*0.2
            color: {
                if(myRect.parasite === 3){return Qt.lighter("black")}
                else {return Qt.darker(app._colors[holder.avatar1])}
            }

            Image{
                width: parent.width*0.65; height: parent.height*0.8
                anchors.centerIn: parent
                source: {
                    if(myRect.parasite === 3) {return "../images/avatars/Parasites/parasite.png"}
                    else if(myRect.human1){return "../images/avatars/heads/player"+holder.avatar1+".png"}
                    else{return "../images/avatars/heads/clone"+holder.avatar1+".png"}
                }
            }
        }
        Rectangle{
            id: p2Rect
            anchors {bottom: parent.bottom; right: parent.right}
            width: parent.width*0.4; height: width
            border {width: 2; color: "black"}
            radius: width*0.2
            color: {
                if(myRect.parasite>-1){
                    if (myRect.parasite === 2){return "black"}
                    else {return "grey"}
                }
                else {return Qt.darker(app._colors[holder.avatar2])}
            }
            Image{
                width: parent.width*0.65; height: parent.height*0.8
                anchors.centerIn: parent
                source: {
                    if(myRect.parasite>-1){return "../images/avatars/Parasites/parasite.png"}
                    else if(myRect.human2){return"../images/avatars/heads/player"+holder.avatar2+".png"}
                    else{return "../images/avatars/heads/clone"+holder.avatar2+".png"}
                }
            }
        }
        Rectangle{  //topright
            id: a1Rect
            anchors {top: parent.top; right: parent.right}
            width: parent.width*0.4; height: width
            border {width: 2; color: "white"}
            color: "firebrick"
            radius: width*0.1

            property string img
            Image{
                anchors.centerIn: parent
                width: parent.width*0.8; height: width
                source: parent.img
            }
        }
        Rectangle{  //right
            id: a2Rect
            anchors {bottom: parent.bottom; right: parent.right}
            width: parent.width*0.6; height: parent.height*0.9
            color: "#00000000"

            property string img

            Image{
                anchors.centerIn: parent
                width: parent.width*0.8; height: parent.height*0.8
                source: parent.img
            }
        }
        Rectangle{  //botleft
            id: a3Rect
            anchors {left: parent.left; bottom: parent.bottom}
            width: parent.width*0.4; height: width
            border {width: 2; color: "white"}
            color: "firebrick"
            radius: width*0.1

            visible: false

            property string img
            Image{
                anchors.centerIn: parent
                width: parent.width*0.8; height: width
                source: parent.img
            }
        }
        Grid{
            anchors {bottom: parent.bottom; left: parent.left}
            spacing: 0
            columns: 2
            Repeater{
                model: myRect.demage
                delegate: Image{
                    width: holder.width*0.2; height: width
                    source: "../images/rooms/icons/dislikeico.png"
                }
            }
        }
        Grid{
            anchors {verticalCenter: parent.verticalCenter; left: parent.horizontalCenter}
            spacing: 3
            columns: 2
            Repeater{
                model: (myRect.pList.length - 1)*2
                delegate: Rectangle{
                    property int player: index% (myRect.pList.length - 1)
                    property int human: index/ (myRect.pList.length - 1)
                    property int avatar: app.avatars[player]

                    width: holder.width*0.2; height: width
                    border {width: 1; color: "black"}
                    radius: width*0.2
                    color: Qt.darker(app._colors[avatar])
                    visible: myRect.pList[player][human]
                    Image{
                        anchors.centerIn: parent
                        width: parent.width*0.65; height: parent.height*0.8
                        source: if(parent.human){"../images/avatars/heads/player"+parent.avatar+".png"} else{"../images/avatars/heads/clone"+parent.avatar+".png"}
                    }
                }
            }
            Repeater{
                model: if(myRect.pList.length){return 2} else {return 0}
                delegate: Rectangle{

                    property int number:{
                        if(index === 1){return myRect.pList[myRect.pList.length- 1][1]}
                        else {return myRect.pList[myRect.pList.length- 1][0]}
                    }

                    width: holder.width*0.2; height: width
                    border {width: 1; color: "black"}
                    radius: width*0.2
                    color: {if (index === 1) {return "black"} else {return "grey"}}
                    visible: number

                    Image{
                        anchors.centerIn: parent
                        width: parent.width*1; height: parent.height*0.8
                        source: "../images/avatars/Parasites/parasite.png"
                    }
                    Text{
                        font {bold: true; pixelSize: parent.width*0.4}
                        anchors {bottom: parent.bottom; right: parent.right}
                        color: "green"
                        text: parent.number
                    }
                }
            }
        }
    }
}

