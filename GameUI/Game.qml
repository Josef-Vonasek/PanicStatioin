import QtQuick 2.4
import QtQuick.Window 2.2
import QtGraphicalEffects 1.0
import ParanoiaEngine 1.0


App{
    id: app

    width: 1650; height: 900


    property variant _colors: ["green", "purple", "orange", "white", "red", "blue"]
    property int actionModel: 0

    focus: true

    Keys.onPressed: {
        if (event.key === Qt.Key_Escape || (event.key === Qt.Key_F4 && event.modifiers === Qt.AltModifier )) {
            _close()
        }
    }

    /*
    property variant parasites: [[[11, 13], 1, 0], [[11, 13], 4, 1], [[11, 13], 6, 2], [[12, 14], 1, 0]]
    property variant blood: [0,0,0,1,3,5]
    property int countBlood: 6
    property variant hitPoints: [[1, 4], [2, 3], [1, 1], [1, 1], [1, 1], [1, 1]]
    property int me: 0
    property variant positions: [[[11, 13],[11,13]], [[11, 13],[11,13]],[[11, 13],[11,13]],[[11, 13],[11,13]],[[11, 13],[11,13]],[[11, 13],[11,13]]]
    property variant avatars: [0, 2, 4, 1, 5, 3]
    property variant cardsOnBoard: [[true, true, false, true], [true, false, false, false], [true, false, false, false], [true, false, false, false], [true, false, false, false], [true, false, false, false]]
    property variant names: ["Anthony", "Bob", "Bob", "Bob", "Bob", "Bob"]
    property variant ammos: [5, 6, 6, 6, 6, 6]
    property variant cards: [8, 5, 5, 5, 5, 5]
    property variant connections: [true, true, true, true, true, false]
    property variant cardsInHand: [["Gas", 1], ["Vest", 2], ["FirstAid", 2], ["FirstAid", 2], ["FirstAid", 2], ["FirstAid", 2], ["FirstAid", 2], ["FirstAid", 2], ["FirstAid", 2], ["FirstAid", 2], ["FirstAid", 2], ["FirstAid", 2], ["FirstAid", 2]]
    property int actionPoints: 4
    property string nextRoom: "room1"
    property variant meeting: [[true, true, 2], [true, false, 3], [true, false, 0], [false, true, 4], [true, true, 5], [1, 2, 5]]
    property int itemCardsLeft: 5
    property int timeTo: 120
    property int actionsLeft: 5
    property int parasiteTurn: 5
    property int playing: 3
    property int openedDoor: 1


    Component.onCompleted: {for(var i=0; i<6; i++){spawnPlayer(i)}
        newRoom(11, 13, "Reactor", 0, false); newRoom(12, 14, "Room5", 1, true);
        useCard(2, "riffle");
        drawCard(2, 1);
        _throwGrenade(1, [0, 1]);
        _throwGrenade(1, [0, 1]);
    }


    property variant _margins: [
        [boardItem.cardY*0.09, boardItem.cardX*0.09],
        [boardItem.cardY*0.09, boardItem.cardX/2],
        [boardItem.cardY*0.09+20, boardItem.cardX/3],
        [boardItem.cardY*0.75, boardItem.cardX*0.09],
        [boardItem.cardY*0.75, boardItem.cardX/2],
        [boardItem.cardY*0.75-20, boardItem.cardX/3]
    ]    

    */
    signal newRoom(int y, int x, string img, int reversed, bool used)
    signal myStatus(variant pos, variant zivoty, int img, variant vylozeno, string jmeno, int naboje)
    signal placeRoom(int y, int x, int prevratit, int jm, int clovek)

    signal pickPlayer(variant actions, string currentRoom)
    onPickPlayer: {
        blocker.pickPlayer(actions, currentRoom)
    }
    // ----

    signal disableMovement()
    onDisableMovement: {
        overLay.animate= false
        figureAnimate.start()
    }

    // ----

    signal newTurn(int player)
    onNewTurn: blocker.newTurn()

    // ----

    signal useCard(int jm, string img)
    onUseCard: {
        actionsModel.append({"_name": "useCard", "_player1": jm, "_human1": 1, "_player2": 0, "_human2": 0, "_demage": 0, "_img": img, "_paras": -1})
        actionsView.newItem()


    }
    // ---
    signal parasiteMovement(variant zraneni)
    onParasiteMovement: {
        if(zraneni[app.me][0] !== 0){blocker.coverPlayer(-1, 0, zraneni[app.me][0])}
        if(zraneni[app.me][1] !== 0){blocker.coverPlayer(-1, 1, zraneni[app.me][1])}
    }

    signal parasiteAttackResult(variant zraneni)
    onParasiteAttackResult: {

        actionsModel.append({"_name": "parasiteAttack", "_player1": 0, "_human1": 0, "_player2": 0, "_human2": 0, "_demage": 0, "_img": "", "_paras": 3})
        actionsView.newItem()
        actionsView.currentItem.pList = zraneni
    }
    // ---
    signal endGame(bool win)
    onEndGame: blocker.endGame(win)

    // ---
    signal newItem(string name)
    onNewItem: {
        newCard.draw(name)
    }

    // ---
    signal turnAround(int _y, int _x)
    onTurnAround: {
        var pos= _y*boardItem.columns + _x
        roomsGrid.children[pos].turnAround()
    }
    // ---
    signal scanAllPlayers(int jm, int clovek, int nakazeni)
    onScanAllPlayers: {
        actionsModel.append({"_name": "scan", "_player1": jm, "_human1": clovek, "_player2": 0, "_human2": 0, "_demage": 0, "_img": "", "_paras": -1})
        actionsView.newItem()

        blocker.scanPlayers(nakazeni)
    }

    // ---
    signal changeCards (int clovek)
    onChangeCards: {
        blocker.changeCards(clovek)
    }
    signal changingCards(int jm, int clovek, int jm1, int clovek1)
    onChangingCards: {
        if(jm1 === app.me){
            blocker.changeCards(clovek1)
        }
        actionsModel.append({"_name": "changingCards", "_player1": jm, "_human1": clovek, "_player2": jm1, "_human2": clovek1, "_demage": 0, "_img": "", "_paras": -1})
        actionsView.newItem()
    }

    signal allCardsChanged(string card)
    onAllCardsChanged: {
        hisCard.img= card
        pickCardTimer.start()
    }    

    //----
    signal tryMove(int _y, int _x)
    onTryMove: {
        var pos= _y*boardItem.columns + _x
        boardItem.children[0].children[pos].move= true
    }

    // ---
    signal movePlayer(int _y, int _x, int jm, int clovek)

    // ---

    signal drawCard(int jm, int clovek)
    onDrawCard: {
        actionsModel.append({"_name": "drawCard", "_player1": jm, "_human1": clovek, "_player2": 0, "_human2": 0, "_demage": 0, "_img": "", "_paras": -1})
        actionsView.newItem()
    }

    // ---
    signal burn(int jm)
    onBurn: {
        actionsModel.append({"_name": "burn", "_player1": jm, "_human1": 1, "_player2": 0, "_human2": 0, "_demage": 0, "_img": "", "_paras": -1})
        actionsView.newItem()
    }
    // ---
    signal heal(int jm, int clovek)
    onHeal: {
        if (jm === app.me){greenAnimation.start()}
        actionsModel.append({"_name": "heal", "_player1": jm, "_human1": clovek, "_player2": 0, "_human2": 0, "_demage": 0, "_img": "", "_paras": -1})
        actionsView.newItem()
    }
    // ---
    signal tryHeal(int clone)
    onTryHeal: blocker.healPlayer(clone)

    // ---
    signal healPlayer(int jm)
    onHealPlayer: {
        if (jm === app.me){greenAnimation.start()}
        actionsModel.append({"_name": "useCard", "_player1": jm, "_human1": 1, "_player2": 0, "_human2": 0, "_demage": 0, "_img": "FirstAid", "_paras": -1})
        actionsView.newItem()
    }


    // ---
    signal openDoors(int jm, int clovek)
    onOpenDoors: {
        actionsModel.append({"_name": "openDoors", "_player1": jm, "_human1": clovek, "_player2": 0, "_human2": 0, "_demage": 0, "_img": "", "_paras": -1})
        actionsView.newItem()
    }

    // ---
    signal throwGrenade(int jm, int clovek, variant _pList)
    onThrowGrenade: {
        var d= _pList[app.me]
        if(d[0] || d[1]){ redAnimation.start()}
        actionsModel.append({"_name": "throwGrenade", "_player1": jm, "_human1": clovek, "_player2": 0, "_human2": 0, "_demage": 0, "_img": "", "_paras": -1})
        actionsView.newItem()
        actionsView.currentItem.pList = _pList
    }
    // ---

    signal stabPlayer(int jm, int jmT, int clovekT, int poskozeni)
    onStabPlayer: {
        if (jmT === app.me && poskozeni){redAnimation.start()}
        actionsModel.append({"_name": "stab", "_player1": jm, "_human1": 1, "_player2": jmT, "_human2": clovekT, "_demage": poskozeni, "_img": "knifeico", "_paras": -1})
        actionsView.newItem()
    }

    signal stabParasite(int jm, int parasite, int poskozeni)
    onStabParasite: {
        actionsModel.append({"_name": "stab", "_player1": jm, "_human1": 1, "_player2": 0, "_human2": 0, "_demage": poskozeni, "_img": "knifeico", "_paras": parasite})
        actionsView.newItem()
    }

    // ---

    signal shootPlayer(int jm, int jmT, int clovekT, variant pohyb, int poskozeni)
    onShootPlayer: {
        if(jmT === app.me){blocker.coverPlayer(jm, clovekT, poskozeni)}
    }

    signal shootResult(int jm, int jmT, int clovekT, int poskozeni)
    onShootResult: {
        actionsModel.append({"_name": "shoot", "_player1": jm, "_human1": 0, "_player2": jmT, "_human2": clovekT, "_demage": poskozeni, "_img": "gunico", "_paras": -1})
        actionsView.newItem()
    }

    signal shootParasite(int jm, int parasite, variant pohyb, int poskozeni)
    onShootParasite: {
        actionsModel.append({"_name": "shoot", "_player1": jm, "_human1": 0, "_player2": 0, "_human2": 0, "_demage": poskozeni, "_img": "gunico", "_paras": parasite})
        actionsView.newItem()
    }

    // ---
    signal scanPlayer(int jm, int clovek, int jm1, int clovek1, variant blood, variant items)
    onScanPlayer: {
        actionsModel.append({"_name": "palmScan", "_player1": jm, "_human1": clovek, "_player2": jm1, "_human2": clovek1, "_demage": 0, "_img": "palmscanico", "_paras": -1})
        actionsView.newItem()

        if(jm === app.me){blocker.scanPlayer(blood, items)}
    }


    signal spawnPlayer(int jm)
    onSpawnPlayer: {
        var i0= jm
        var i1= jm+ connections.length
        overLay.children[i0].spawn()
        overLay.children[i1].spawn()
        if(jm === app.me){spawnRect.visible= false}
    }

    onNewRoom: {
        var pos= y*boardItem.columns + x;
        boardItem.children[0].children[pos].placeRoom(reversed, img, used)
    }

    onPlaceRoom: {
        var pos= y*boardItem.columns + x
        roomsGrid.children[pos].placeRoom(prevratit, "", false)
        actionsModel.append({"_name": "explore", "_player1": jm, "_human1": clovek, "_player2": 0, "_human2": 0, "_demage": 0, "_img": app.nextRoom, "_paras": -1})
        actionsView.newItem()
    }

    FontLoader{
        id: fontFace
        source: "../Font/FaceYourFears.ttf"
    }

    Rectangle {
        id: root
        anchors.fill: parent
        property string name: "PanicStation"        


        Rectangle {
            id: something
            anchors.fill: parent
            color: "#a4a4a4"
            Image { source: "../images/rooms/icons/hexatexture.png"; fillMode: Image.Tile; anchors.fill: parent; opacity: 1 }
            Rectangle{
                gradient: Gradient {
                    GradientStop {
                        position: 0.026
                        color: "#99000000"
                    }

                    GradientStop {
                        position: 0.256
                        color: "#80525252"
                    }

                    GradientStop {
                        position: 0.653
                        color: "#b3000000"
                    }


                    GradientStop {
                        position: 0.88
                        color: "#e6000000"
                    }
                }
                anchors.fill: parent
            }


            Flickable {
                id: boardFlick
                anchors.fill: parent
                leftMargin: if(contentWidth < app.width){return ((app.width - contentWidth)/2)} else {app.width*0.1}
                rightMargin: if(contentWidth < app.width){0} else {app.width*0.1}
                topMargin: app.height*0.1
                bottomMargin: app.height*0.3
                contentHeight: (boardItem.rows*212) * flickMouse.scaled
                contentWidth: (boardItem.columns*152) * flickMouse.scaled
                contentX: (boardItem.columns*152 - app.width)/2
                contentY: (boardItem.rows*212 - app.height)/2
                rebound: Transition {
                        NumberAnimation {
                            properties: "x,y"
                            duration: 1000
                            easing.type: Easing.OutBounce
                        }
                    }
                flickableDirection: Flickable.HorizontalAndVerticalFlick

                MouseArea{
                    id: flickMouse
                    property double scaled: 1
                    anchors.fill: parent
                    propagateComposedEvents: true
                    onWheel: {
                        if(wheel.angleDelta.y > 0){
                            var _x, _y
                            _x= (boardFlick.contentX + app.width/2)/boardFlick.contentWidth
                            _y = (boardFlick.contentY + app.height/2)/boardFlick.contentHeight
                            scaled += 0.1
                            boardItem.scale+= 0.1
                            boardFlick.contentX= boardFlick.contentWidth*_x - app.width/2
                            boardFlick.contentY= boardFlick.contentHeight*_y - app.height/2
                        } else if (scaled > 0.4) {
                            _x= (boardFlick.contentX + app.width/2)/boardFlick.contentWidth
                            _y = (boardFlick.contentY + app.height/2)/boardFlick.contentHeight
                            scaled -= 0.1
                            boardItem.scale -= 0.1
                            boardFlick.contentX= boardFlick.contentWidth*_x - app.width/2
                            boardFlick.contentY= boardFlick.contentHeight*_y - app.height/2
                        }
                    }
                }

                Item{
                    id: boardItem

                    property int cardY: 210
                    property int cardX: 150

                    property int columns: 27
                    property int rows: 25

                    x: 0; y:0

                    transformOrigin: Item.TopLeft


                    anchors.fill: parent

                    Component{
                        id: boardCard
                        Rectangle{
                            id: rect
                            radius: 5
                            width: boardItem.cardX
                            height: boardItem.cardY
                            color: "#195b5b5b"
                            border.width: 2
                            clip: true

                            transform: Rotation { origin.x: width/2; origin.y: height/2; angle: _rotation}

                            property string image: ""
                            property bool active: false
                            property int _rotation: 0
                            property bool isShowed: false
                            property bool move: false

                            property int _y: index/boardItem.columns
                            property int _x: index%boardItem.columns

                            signal showRoom (int rotate, string img, bool showing)
                            signal placeRoom (int rotate, string img, bool used) //rotate je ve skutečnosti pouze 1/0 (bool)
                            signal turnAround()


                            onTurnAround:{
                                var img = image.slice(0, -4)
                                image = image.replace(".png", "n.png")
                            }

                            onShowRoom: {
                                if (showing){
                                    image= img;
                                    _rotation = rotate * 180;
                                    isShowed = true;
                                }
                                else{
                                    image= "";
                                    isShowed = false
                                }
                            }
                            onPlaceRoom: {
                                var ending
                                if(used){ending = "n.png"} else {ending= ".png"}
                                if (!img){image= nextRoomImage.source}
                                else {image = "../images/rooms/rooms/" + img + ending}
                                _rotation = rotate * 180;
                                active= true;
                                isShowed= false;
                            }


                            MouseArea{
                                id: roomMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                onClicked: {
                                    if (!parent.active && mDNextRoomHolder.selected) {
                                        app._placeRoom(app.human, _y, _x, (mDNextRoomHolder.state === "reset" ? 0 : 1))
                                    }
                                    else if(parent.active && app.positions[app.me][app.human][0] === _y && app.positions[app.me][app.human][1]=== _x){                                        
                                        app._newMeeting([0, 0])
                                        app._pickPlayer(app.human)
                                    }
                                    else if(parent.move){
                                        app._movePlayer(_y, _x, app.human)
                                        parent.move= false
                                    }

                                }
                                onEntered: {
                                    if (!parent.active && mDNextRoomHolder.selected && app.roomCardsLeft){
                                        parent.showRoom((mDNextRoomHolder.state === "reset" ? 0 : 1), nextRoomImage.source, true)
                                    }
                                    else if(parent.active && !(app.positions[app.me][app.human][0] === _y && app.positions[app.me][app.human][1] === _x)){
                                        app._tryMove(_y, _x, app.human)
                                    }
                                }
                                onExited: {
                                    if (!parent.active){
                                        parent.showRoom((mDNextRoomHolder.state === "reset" ? 0 : 1), nextRoomImage.source, false)                                    
                                    }
                                    else if(parent.move){
                                        parent.move= false
                                    }
                                }

                            }

                            Rectangle{
                                visible: parent.isShowed
                                color: "#80ffffff"
                                anchors.fill: parent
                                radius: 5
                            }

                            Image{
                                id: im1
                                anchors.margins: 5
                                anchors.fill: parent
                                source: rect.image
                            }
                            Image{
                                id: moveImage
                                rotation: parent._rotation
                                visible: parent.move && roomMouse.containsMouse
                                width: parent.width*0.35; height: parent.height*0.25
                                anchors.centerIn: parent
                                source: "../images/rooms/icons/moveico.png"
                            }



                        }
                    }


                    Grid{
                        id: roomsGrid
                        columns: boardItem.columns
                        spacing: 2

                        Repeater{
                            id: repeater
                            model: boardItem.columns*boardItem.rows
                            delegate: boardCard

                        }
                    }

                   Rectangle {

                        id: overLay
                        anchors.fill: parent
                        color: "#00ffffff"

                        property bool animate: true

                        signal movePlayer(int player, bool human, int y, int x)


                        Timer{
                            id: figureAnimate
                            interval: 500; running: false; repeat: false
                            onTriggered: overLay.animate= true
                        }

                        Repeater{
                            model: app.connections.length*2
                            delegate: figure
                        }

                        Component{
                            id: figure
                            Rectangle{
                                id: figureItem

                                width: 59*0.7; height: 57*0.7
                                x: -100; y:-100
                                radius: width/2
                                border {width: 1; color: "black"}

                                property int human: index>= app.connections.length
                                property int player: {if(!human){index}else{index - app.connections.length}}

                                property int _x: app.positions[player][human][1]
                                property int _y: app.positions[player][human][0]

                                property variant _margins: [
                                    [boardItem.cardY*0.08, boardItem.cardX*0.1],
                                    [boardItem.cardY*0.08, boardItem.cardX*0.48],
                                    [boardItem.cardY*0.08 + height*0.8, boardItem.cardX*0.1],
                                    [boardItem.cardY*0.08 + height*0.8, boardItem.cardX*0.48],
                                    [boardItem.cardY*0.73, boardItem.cardX*0.1],
                                    [boardItem.cardY*0.73, boardItem.cardX*0.48],
                                ]

                                state: "default"
                                states: [
                                    State{
                                        name: "default"
                                        PropertyChanges{
                                            target: figureItem
                                            visible: false
                                            x: -100; y: -100
                                        }
                                    },
                                    State{
                                        name: "spawned"
                                        PropertyChanges{
                                            target: figureItem
                                            visible: app.hitPoints[figureItem.player][figureItem.human]
                                            x: (figureItem._x)*(boardItem.cardX+2) + figureItem._margins[figureItem.player][1] + width/2* figureItem.human
                                            y: (figureItem._y)*(boardItem.cardY+2) + figureItem._margins[figureItem.player][0]
                                        }
                                    }

                                ]

                                signal spawn()

                                onSpawn: {
                                    state= "spawned"
                                }

                                gradient: Gradient {
                                    GradientStop {
                                        position: 0
                                        color: Qt.lighter(app._colors[app.avatars[figureItem.player]])
                                    }

                                    GradientStop {
                                        position: 1
                                        color: Qt.darker(app._colors[app.avatars[figureItem.player]])
                                    }


                                }

                                visible: false
                                Behavior on y {
                                    PropertyAnimation {
                                        easing.type: Easing.OutQuad
                                        target: figureItem
                                        property: "y"
                                        duration: 600
                                    }
                                }
                                Behavior on x {
                                    PropertyAnimation {
                                        easing.type: Easing.OutQuad
                                        property: "x"
                                        duration: 600
                                    }
                                }

                                Image{
                                    id: img
                                    width: parent.width*0.6; height: parent.height*0.8
                                    anchors.centerIn: parent
                                    source: {
                                        var s                                        
                                        if(human){s = "player"+app.avatars[player]}
                                        else{s = "clone"+app.avatars[player]}
                                        return "../images/avatars/heads/"+ s +".png"
                                    }
                                }

                                MouseArea{
                                    visible: false
                                    anchors.fill: parent
                                    onClicked:{
                                        app.changingCards(0,1,app.me,1)
                                    }
                                }
                            }
                        }
                        Repeater{
                            model: app.parasites.length
                            delegate: parasiteF
                        }

                        Component{
                            id: parasiteF
                            Rectangle{
                                id: parasiteFRect
                                x: (_x)*(boardItem.cardX+2) + _margin[1] + type*(width)
                                y: (_y)*(boardItem.cardY+2) + _margin[0]

                                width: 59*0.7; height: 57*0.7
                                radius: width/2
                                border {width: 2; color: "grey"}

                                property int count: app.parasites[index][1]
                                property int type: app.parasites[index][2]

                                property int _x: app.parasites[index][0][1]
                                property int _y: app.parasites[index][0][0]

                                property variant _margin: [boardItem.cardY*0.73 - height*0.8, boardItem.cardX*0.1]

                                gradient: Gradient {
                                    GradientStop {
                                        position: 0
                                        color: if (parasiteFRect.type === 2){return "black"} else {return "white"}
                                    }

                                    GradientStop {
                                        position: 1
                                        color: if (parasiteFRect.type === 0){return "white"} else {return "black"}
                                    }

                                }

                                Behavior on y {
                                    enabled: overLay.animate
                                    PropertyAnimation {
                                        easing.type: Easing.OutQuad
                                        property: "y"
                                        duration: 600
                                    }
                                }
                                Behavior on x {
                                    enabled: overLay.animate
                                    PropertyAnimation {
                                        easing.type: Easing.OutQuad
                                        property: "x"
                                        duration: 600
                                    }
                                }

                                Text{
                                    anchors {right: parent.right; bottom: parent.bottom}
                                    font {family: fontFace.name; bold: true; pixelSize: parent.width*0.5}
                                    color: "brown"
                                    text: parent.count
                                }

                                Image{
                                    id: img
                                    width: parent.width*0.6; height: parent.height*0.8
                                    anchors.centerIn: parent
                                    source: "../images/avatars/Parasites/parasite.png"
                                }

                                MouseArea{
                                    anchors.fill: parent
                                    onClicked:{
                                        console.log("kliknul jsem na parazita")
                                    }
                                }
                            }
                        }
                    }
                }
            }


            Rectangle {
                id: mapDeck
                x: 5
                y: 5
                width: app.width * 0.112; height: app.height * 0.31
                color: "#262626"
                border.width: 2
                radius: 15
                border.color: "#000000"
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.margins: 5

                visible: if(app.roomCardsLeft) {true} else {false}

                MouseArea{
                    id: mDClick
                    anchors.fill: parent
                }

                Rectangle{
                    id: mDTurnArrowHolder

                    width: parent.width/6; height: width
                    radius: width/2
                    anchors.bottomMargin: width/3
                    anchors.rightMargin: width
                    anchors.bottom: parent.bottom
                    anchors.right: parent.right
                    color: parent.color
                    border.color: "#c6c6c6"
                    border.width: 2
                    Image{
                        id: turnArrowImage
                        source: "../images/rooms/icons/arrow.png"
                        anchors.centerIn: parent
                        height: parent.height/2; width: height
                    }
                    MouseArea{
                        anchors.fill: parent
                        onClicked: mDNextRoomHolder.turnAround()
                    }
                }

                Rectangle{
                    id: mDCardLeftHolder

                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.bottomMargin: width/3
                    anchors.leftMargin: width
                    border.width: 2
                    radius: width/3
                    width: mDTurnArrowHolder.width; height: width
                    border.color: "white"
                    color: parent.color

                    Text{
                        id: cardLeftText

                        text: app.roomCardsLeft
                        anchors.centerIn: parent
                        color: "white"
                        font {bold: true; family: fontFace.name}
                    }
                }

                RectangularGlow {
                        id: mDGlow

                        visible: false
                        anchors.centerIn: mDNextRoomHolder
                        width: mDNextRoomHolder.width; height: mDNextRoomHolder.height
                        glowRadius: 10
                        spread: 0.2
                        color: "yellow"
                        cornerRadius: mDNextRoomHolder.radius + glowRadius
                    }

                Rectangle{
                    id: mDNextRoomHolder

                    signal turnAround
                    property bool selected: false

                    color: "#00000000"
                    width: parent.width/1.2; height: parent.height/1.3
                    anchors.top: parent.top
                    anchors.topMargin: 10
                    anchors.horizontalCenter: parent.horizontalCenter
                    clip: false

                    state: "reset"
                    states: [
                        State{
                            name: "reset"
                            PropertyChanges {target: mDNextRoomHolder; rotation: 0}
                            PropertyChanges {target: mDGlow; rotation: 0}
                        },
                        State {
                            name: "rotate"
                            PropertyChanges { target: mDNextRoomHolder; rotation: 180}
                            PropertyChanges { target: mDGlow; rotation: 180}
                        }
                    ]

                    transitions: Transition {
                        RotationAnimation { duration: 500; direction: RotationAnimation.Counterclockwise }
                    }

                    onTurnAround: {
                        state = (state === "reset" ? "rotate" : "reset")
                    }

                    Image{
                        id: nextRoomImage
                        anchors.fill: parent
                        source: "../images/rooms/rooms/"+app.nextRoom+".png"
                    }
                    MouseArea{
                        anchors.fill: parent
                        onClicked: {
                            if (parent.selected == true){parent.selected = false; mDGlow.visible= false}
                            else {parent.selected = true; mDGlow.visible= true}
                        }
                    }
                }
            }

            Item{
                id: newCard
                visible: false
                x: app.width * 0.05; y: app.height * 0.53
                width: app.width*0.08; height: app.height * 0.2

                property variant cards: []

                signal draw(string name)

                onDraw: {
                    cards.push("../images/rooms/cards/" + name + ".png")
                    cardsChanged()
                    if(!newCardTimer.running){
                        newCardTimer.start()
                        newCardAnimation1.start()
                    }
                }

                SequentialAnimation{
                    id: newCardAnimation1
                    PropertyAction{ target: newCard; property: "opacity"; value: "0"}
                    PropertyAction{ target: newCard; property: "visible"; value: "true"}
                    NumberAnimation{ target: newCard; property: "opacity"; to: 1; duration: 1000}
                    PropertyAnimation{ target: newCardGlow; property: "color"; to: "blue"; duration: 500}
                    PropertyAnimation{ target: newCardGlow; property: "color"; to: "darkBlue"; duration: 900}
                }
                SequentialAnimation{
                    id: newCardAnimation2
                    NumberAnimation{ target: newCard; property: "opacity"; to: 0; duration: 100}
                    NumberAnimation{ target: newCard; property: "opacity"; to: 1; duration: 900}
                    PropertyAnimation{ target: newCardGlow; property: "color"; to: "blue"; duration: 500}
                    PropertyAnimation{ target: newCardGlow; property: "color"; to: "darkBlue"; duration: 900}
                }
                SequentialAnimation{
                    id: newCardAnimation3
                    PropertyAnimation{ target: newCard; property: "opacity"; to: "0"; duration: 500}
                    PropertyAction{ target: newCard; property: "visible"; value: "false"}
                }

                Timer {
                    id: newCardTimer
                    interval: 2500; running: false; repeat: true
                    onTriggered: {
                        newCard.cards.shift()
                        newCard.cardsChanged()
                        if(!newCard.cards.length){
                            stop()
                            newCardAnimation3.start()
                        }
                        else{
                            newCardAnimation2.start()
                        }
                    }
                }

                RectangularGlow {
                    id: newCardGlow
                    anchors.fill: parent
                    glowRadius: width* 0.1
                    spread: 0.3
                    color: "darkBlue"
                    cornerRadius: glowRadius
                }
                Image{
                    id: newCardImage
                    anchors.fill: parent
                    opacity: 0.6
                    source: if(newCard.cards.length){  newCard.cards[0]  } else {""}
                }


            }

            Rectangle {
                id: playerSelected

                signal changePlayer(int index)
                signal hide

                property int player: 0
                property variant cardNames: ["knife", "card", "riffle", "scope"]

                width: app.width * 0.28; height: app.height* 0.12
                color: "#363636"
                radius: 15
                clip: false
                visible: false
                anchors.rightMargin: 5
                anchors.topMargin: 5
                border.width: 2
                anchors.top: parent.top
                anchors.right: parent.right

                onChangePlayer: {
                    visible = true;
                    player= index;

                }
                onHide: {
                    visible= false
                    players.selected.state= "default"
                }

                MouseArea{
                    anchors.fill: parent
                    onClicked: parent.hide()
                }


                Rectangle{
                    id: pSHeadHolder

                    width: parent.width * 0.2; height: parent.height * 0.8
                    color: "#2e4b1f"
                    radius: width/8
                    border {width: 2; color: "black"}
                    gradient: Gradient {
                        GradientStop {
                            position: 0
                            color: "black"
                        }

                        GradientStop {
                            position: 1
                            color: Qt.darker(app._colors[app.avatars[playerSelected.player]])
                        }


                    }
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.rightMargin: 10

                    Image{
                        id: pSHeadImage
                        width: parent.width*0.6; height: parent.width*0.8
                        source: "../images/avatars/heads/player"+ app.avatars[playerSelected.player] +".png"
                        anchors.centerIn: parent
                    }

                }


                Row{
                    id: pSPlayerInfo1
                    height: parent.height/2     //50
                    anchors.verticalCenterOffset: -height/3.33
                    spacing: height/5
                    anchors.leftMargin: spacing
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.right: pSHeadHolder.left
                    anchors.left: parent.left

                    ListModel {
                        id: cardsUsedModel
                        ListElement {
                            name: 0
                            image: "Knife"
                        }

                        ListElement {
                            name: 1
                            image: "Card"
                        }

                        ListElement {
                            name: 2
                            image: "Riffle"
                        }

                        ListElement {
                            name: 3
                            image: "Scope"
                        }
                    }

                    Repeater {
                        model: cardsUsedModel

                        Rectangle {
                            property alias source: pSCardsUsedImage.source
                            width: playerSelected.width * 0.12; height: playerSelected.height * 0.5
                            radius: width/10
                            border.width: 1; border.color: Qt.darker(color)
                            color: {if(app.cardsOnBoard[playerSelected.player][name]){return "#2e4b1f"} else{return playerSelected.color}}
                            Image{
                                id: pSCardsUsedImage
                                source: "../images/rooms/icons/"+image+".png"
                                anchors.centerIn: parent
                                width: parent.width * 0.8; height: parent.height * 0.8
                            }

                        }
                    }

                    Rectangle{
                        id: pSCardsInHand

                        property int cards: app.cards[playerSelected.player]

                        width: playerSelected.width * 0.13; height: playerSelected.height * 0.5
                        color: playerSelected.color
                        clip: true
                        Image{
                            source: "../images/rooms/icons/cards.png"
                            anchors.fill: parent
                        }
                        Rectangle{
                            width: parent.width /2; height: width
                            anchors.centerIn: parent
                            color: "#80ffffff"
                            radius: Math.round(width/2)
                            border.width: 1
                            border.color: "#767676"


                            Text{
                                text: pSCardsInHand.cards
                                anchors.centerIn: parent
                                color: "black"
                                font {bold: true; family: fontFace.name; pixelSize: parent.height * 0.7}
                            }
                        }

                    }



                }

                Row{
                    id: pSPlayerInfo2
                    height: parent.height/10*3     //30
                    anchors.leftMargin: height/3
                    anchors.topMargin: height/6
                    anchors.top: pSPlayerInfo1.bottom
                    anchors.left: parent.left
                    Repeater{
                        id: pSHumanHP
                        model: app.hitPoints[playerSelected.player][1]
                        Image{
                            width: playerSelected.width * 0.07; height: playerSelected.height * 0.3
                            source: "../images/useful/Heart00.png"
                        }
                    }
                    Repeater{
                        id: pSCloneHP
                        model: app.hitPoints[playerSelected.player][0]
                        Image{
                            width: playerSelected.width * 0.07; height: playerSelected.height * 0.3
                            source: "../images/useful/Heart01.png"
                        }
                    }
                    }

                Rectangle{
                    id: pSAmmo

                    property int ammo: app.ammos[playerSelected.player]

                    width: playerSelected.width * 0.08; height: playerSelected.height * 0.3
                    color: playerSelected.color
                    x: playerSelected.width * 0.63
                    anchors.verticalCenter: pSPlayerInfo2.verticalCenter

                    Image{
                        source: "../images/rooms/icons/ammo.png"
                        anchors.fill: parent
                    }

                    Text{
                        anchors.centerIn: parent
                        font {bold: true; family: fontFace.name; pixelSize: parent.height * 0.7}
                        color: "#ccffffff"
                        text: parent.ammo
                    }
                }
            }


            Item {
            id: players

            width: app.width/20.5   //80
            anchors.rightMargin: 10
            y: app.height*0.135
            anchors.right: parent.right

            property variant selected: children[0].children[0]

            Column{
                anchors.fill: parent
                spacing: 10
                Repeater{
                    id: pRepeater
                    model: app.connections.length
                    Rectangle{
                        id: self

                        visible: pCloneHP.visible || pHumanHP.visible
                        width : players.width; height: width
                        color: "#226d07"
                        property string _color: if(app.playing === index) {"#226d07"} else {"#262626"}
                        border.width: 2
                        radius: width/8

                        state: "default"
                        states:[
                            State{
                                name: "default"
                                PropertyChanges{target: self; color: self._color}
                            },
                            State{
                                name: "selected"
                                PropertyChanges{target: self; color: Qt.lighter(self._color)}
                            }

                        ]

                        Image{
                            id: playerIcon
                            source: "../images/avatars/heads/player"+app.avatars[index]+".png"
                            width: parent.width*0.7; height: parent.height*0.8
                            anchors.centerIn: parent
                            anchors.horizontalCenterOffset: -parent.width/12

                            state: app.connections[index]
                            states: [
                                State{
                                    name: "connected"
                                    PropertyChanges {target: playerIcon; source: "../images/avatars/heads/player"+app.avatars[index]+".png"}
                                },
                                State {
                                    name: "disconnected"
                                    PropertyChanges { target: playerIcon; source: "../images/avatars/heads/player"+app.avatars[index]+"n.png"}
                                }
                            ]
                        }
                        Rectangle{
                            id: pHumanHP
                            visible: app.hitPoints[index][1] > 0
                            anchors.right: parent.right
                            anchors.top: parent.top
                            width: parent.width/2.3; height: width
                            color: "#df1c1c"
                            radius: width/2
                            border.color: "#310505"
                            border.width: 4
                            Text{
                                text: app.hitPoints[index][1]
                                anchors.centerIn: parent
                                font {family: fontFace.name}
                            }
                        }
                        Rectangle{
                            id: pCloneHP
                            visible: app.hitPoints[index][0] > 0
                            anchors.top: pHumanHP.bottom
                            anchors.right: parent.right
                            anchors.topMargin: -7
                            width: parent.width/3; height: width
                            color: "#c51111"
                            radius: width/2
                            border.color: "#310505"
                            border.width: 4
                            Text{
                                text: app.hitPoints[index][0]
                                anchors.centerIn: parent
                                font {family: fontFace.name}
                            }
                        }

                        Image{
                            visible: app.parasiteTurn === index
                            anchors {right: parent.right; bottom: parent.bottom}
                            width: players.width*0.35; height: width
                            source: "../images/rooms/icons/pdrawing.png"
                        }

                        Rectangle{
                            id: doorOpen
                            visible: if(app.openedDoor === index) {doorAnimation.start(); return true} else {doorAnimation.stop(); return false}
                            anchors {verticalCenter: parent.top; right: parent.left}
                            width: parent.width*0.4; height: width
                            color: bar.color
                            border {width: 3; color: "black"}
                            radius: width/2

                            Image{
                                anchors.centerIn: parent
                                width: parent.width*0.6; height: width
                                source: "../images/rooms/icons/doorico.png"
                            }

                            SequentialAnimation {
                                id: doorAnimation
                                loops: Animation.Infinite
                                NumberAnimation { target: doorOpen; property: "opacity"; to: 0.4; duration: 1000 }
                                NumberAnimation { target: doorOpen; property: "opacity"; to: 1; duration: 1000 }
                            }
                        }

                        MouseArea{
                            anchors.fill: parent
                            onClicked: {
                                players.selected.state = "default";
                                parent.state = "selected"
                                players.selected= parent;
                                playerSelected.changePlayer(index);
                            }

                        }
                    }

                }
            }
            }
            Rectangle{
                id: indicator

                anchors {horizontalCenter: parent.horizontalCenter}
                y: parent.height*0.02
                width: parent.width *0.1; height: parent.height*0.1
                border {width:1 ; color: "black"}
                color: "darkGreen"
                radius: height*0.15

                gradient: Gradient {
                    GradientStop {
                        position: 0
                        color:  "white"
                    }

                    GradientStop {
                        position: 1
                        color: "black"
                    }
                }

                Item{
                    id: infoHolder
                    anchors.fill: parent

                    IndicatorComponent{
                        id: iCardsLeft
                        anchors.left: parent.left
                        img: "cardsleftico"
                        txt: app.itemCardsLeft
                    }
                    IndicatorComponent{
                        id: iTimeLeft
                        anchors.horizontalCenter: parent.horizontalCenter
                        img: "timeico"
                        txt: app.timeTo
                    }
                    IndicatorComponent{
                        id: iActionsLeft
                        anchors.right: parent.right
                        img: "handico"
                        txt: app.actionPoints
                    }
                }



                Rectangle{
                    id: endRect
                    anchors.fill: parent
                    gradient: parent.gradient
                    visible: false
                    clip: true
                    radius: parent.radius

                    Text{
                        anchors.centerIn: parent
                        font{bold: true; family: fontFace.name; pixelSize: parent.height*0.35}
                        color: "darkOrange"
                        text: "End Turn"
                    }
                }

                MouseArea{
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: if(app.playing === app.me){app._endTurn(); endRect.visible= false; infoHolder.visible= true}
                    onEntered: if(app.playing === app.me){endRect.visible= true; infoHolder.visible = false}
                    onExited: if(app.playing === app.me){endRect.visible= false; infoHolder.visible = true}
                }

            }

            Rectangle{
                id: spawnRect
                width: parent.width*0.15; height: parent.height*0.08
                border {width: 5; color: "white"}
                radius: height*0.2
                x: parent.width*0.2; y: parent.height*0.02
                color: "grey"

                Text{
                    anchors.centerIn: parent
                    font {bold: true; family: fontFace.name; pixelSize: parent.height * 0.4}
                    text: "Spawn"
                    color: "black"
                }
                MouseArea{
                    anchors.fill: parent
                    onClicked: app._spawn()
                }
            }
        }
        Rectangle{
            id: blocker
            anchors.fill: parent
            color: "#b3000000"
            visible: false

            property string _state: ""


            signal pickPlayer(variant actions, string currentRoom)
            signal changeCards(int meHuman)
            signal healPlayer(int clone)
            signal coverPlayer(int attacker, int humanT, int dmg)
            signal scanPlayer(variant blood, variant items)
            signal scanPlayers(int number)
            signal newTurn()
            signal endGame(bool win)

            onEndGame: {
                _state= "endingGame"
                endThis.endGame(win)
            }

            onPickPlayer: {
                visible= true
                playerPicker.showActions= actions
                playerPicker.meHuman= app.human
                playerPicker.currentRoom= currentRoom
                playerPicker.reset()
                _state= "pickingAction"
            }


            onChangeCards: {
                visible= true

                playerPicker.meHuman= meHuman
                pickCard.sent= false
                playerPicker.reset()
                _state= "pickingAction"

                actionSwitcher.state = "meeting"
                if (app.playing !== app.me || meHuman && !app.cardsOnBoard[app.me][0] || !meHuman && !app.ammos[app.me] || !app.actionPoints){
                    _state = "pickingCard"
                }
            }
            onHealPlayer: {
                if (_state === "cover"){return}
                healPicker.setUp(clone)
                visible= true
                _state= "healingPlayer"
            }
            onCoverPlayer: {
                coverPicker.setUp(attacker, humanT, dmg)
                visible= true
                _state= "cover"

                dangerAnimation.start()
            }
            onScanPlayer: {
                _state= "scanningPlayer"
                visible= true
                playerScan.blood = blood
                playerScan.items = items
            }
            onNewTurn: {
                _state= "newTurn"
                newTurnAnimation.start()
            }
            onScanPlayers: {
                _state = "scanningPlayers"
                playersScan.number = number
                playersScanAnimation.start()
            }

            SequentialAnimation{
                id: newTurnAnimation
                PropertyAction{target: blocker; property: "visible"; value: "true"}
                PropertyAction{target: newTurnHolder; property: "visible"; value: "true"}
                ParallelAnimation{
                    PropertyAnimation{ target: blocker; property: "color"; to: Qt.rgba(0, 0, 255, 0.6); duration: 1000}
                    NumberAnimation{ target: blocker; property: "opacity"; from: 0; to: 1; duration: 500}
                }
                PauseAnimation{ duration: 500}
                ParallelAnimation{
                    PropertyAnimation{ target: blocker; property: "color"; to: "#b3000000"; duration: 1000}
                    NumberAnimation{ target: blocker; property: "opacity"; easing.type: Easing.InExpo; to: 0; duration: 1000}
                }
                PropertyAction{target: blocker; property: "visible"; value: "false"}
                PropertyAction{target: newTurnHolder; property: "visible"; value: "false"}
                PropertyAction{target: blocker; property: "opacity"; value: "1"}
            }

            SequentialAnimation {
                id: dangerAnimation
                loops: Animation.Infinite
                PropertyAnimation { target: blocker; property: "color"; to: Qt.rgba(255, 0, 0, 0.6); duration: 1000 }
                PropertyAnimation { target: blocker; property: "color"; to: Qt.rgba(255, 0, 0, 0.1); duration: 1000 }
            }
            SequentialAnimation {
                id: redAnimation
                PropertyAction{ target: blocker; property: "color"; value: Qt.rgba(0, 0, 0, 0)}
                PropertyAction{ target: bMouse; property: "visible"; value: "false"}
                PropertyAction{ target: blocker; property: "visible"; value: "true"}
                PropertyAnimation { target: blocker; property: "color"; to: Qt.rgba(255, 0, 0, 0.6); duration: 1000 }
                PropertyAnimation { target: blocker; property: "color"; to: Qt.rgba(255, 0, 0, 0.1); duration: 1000 }
                PropertyAction{ target: blocker; property: "visible"; value: "false"}
                PropertyAction{ target: bMouse; property: "visible"; value: "true"}
                PropertyAction{ target: blocker; property: "color"; value: "#b3000000"}
            }
            SequentialAnimation {
                id: blueAnimation
                PropertyAction{ target: blocker; property: "color"; value: Qt.rgba(0, 0, 0, 0)}
                PropertyAction{ target: bMouse; property: "visible"; value: "false"}
                PropertyAction{ target: blocker; property: "visible"; value: "true"}
                PropertyAnimation { target: blocker; property: "color"; to: Qt.rgba(0, 0, 255, 0.6); duration: 1000 }
                PropertyAnimation { target: blocker; property: "color"; to: Qt.rgba(0, 0, 255, 0.1); duration: 1000 }
                PropertyAction{ target: blocker; property: "visible"; value: "false"}
                PropertyAction{ target: bMouse; property: "visible"; value: "true"}
                PropertyAction{ target: blocker; property: "color"; value: "#b3000000"}
            }
            SequentialAnimation {
                id: greenAnimation
                PropertyAction{ target: blocker; property: "color"; value: Qt.rgba(0, 0, 0, 0)}
                PropertyAction{ target: bMouse; property: "visible"; value: "false"}
                PropertyAction{ target: blocker; property: "visible"; value: "true"}
                PropertyAnimation { target: blocker; property: "color"; to: Qt.rgba(0, 255, 0, 0.6); duration: 1000 }
                PropertyAnimation { target: blocker; property: "color"; to: Qt.rgba(0, 255, 0, 0.1); duration: 1000 }
                PropertyAction{ target: blocker; property: "visible"; value: "false"}
                PropertyAction{ target: bMouse; property: "visible"; value: "true"}
                PropertyAction{ target: blocker; property: "color"; value: "#b3000000"}
            }

            MouseArea{
                id: bMouse
                anchors.fill: parent
                hoverEnabled: true
                onClicked: {
                    if (["pickingAction", "healingPlayer", "scanningPlayer", "scanningPlayers"].indexOf(parent._state) !== -1 && actionSwitcher.state !== "meeting"){
                        parent._state = ""
                        parent.visible  = false
                        parent.color= "#b3000000"
                    }
                }

            }
            Item{
                id: endThis
                anchors.fill: parent
                visible: false

                property string name: "win"
                signal endGame(bool win)
                onEndGame: {
                    name= (win ? "win" : "lose")
                    endAnimation.start()
                }
                MouseArea{ anchors.fill: parent}

                SequentialAnimation{
                    id: endAnimation
                    PropertyAction{ target: blocker; property: "color"; value: "transparent"}
                    PropertyAction{ target: blocker; property: "visible"; value: "true"}
                    PropertyAnimation{ target: blocker; property: "color"; to: "white"; duration: 500; easing.type: Easing.OutInQuint}
                    PropertyAction{ target: endThis; property: "opacity"; value: "0"}
                    PropertyAction{ target: endThis; property: "visible"; value: "true"}
                    ParallelAnimation{
                        PropertyAnimation{ target: blocker; property: "color"; to: "transparent"; duration: 500; easing.type: Easing.OutInQuint}
                        NumberAnimation{ target: endThis; property: "opacity"; from: 0; to: 1; duration: 500}
                    }
                    PauseAnimation{ duration: 500}
                    PropertyAction{ target: endImgAll; property: "opacity"; value: "0"}
                    PropertyAction{ target: endImgAll; property: "visible"; value: "true"}
                    ParallelAnimation{
                        NumberAnimation{ target: endImgFront; property: "opacity"; from: 0.5; to: 0; duration: 1000}
                        NumberAnimation{ target: endImgAll; property: "opacity"; from: 0; to: 1; duration: 1000}
                    }
                }

                Rectangle{
                    id: endImgFront
                    anchors.fill: parent
                    color: Qt.rgba(0, 0, 0, 0.5)
                }
                Rectangle{
                    id: endImgAll
                    anchors.fill: parent
                    visible: false
                    color: Qt.rgba(0, 0, 0, 0.3)
                    Text{
                        anchors.centerIn: parent
                        font {bold: true; italic: true; family: fontFace.name; capitalization: Font.AllUppercase; pixelSize: parent.height * 0.35}
                        text: (endThis.name === "win" ? "Victory!" : "Defeat!")
                        color: (endThis.name === "win" ? "darkGreen" : "darkRed")
                    }
                }

                /*
                Image{
                    id: endImgFront
                    anchors.fill: parent
                    source: "../images/rooms/lose/paranoia-"+ endThis.name +"-concept-popredi.png"
                    opacity: 0.5
                }
                Image{
                    id: endImgAll
                    anchors.fill: parent
                    source: "../images/rooms/lose/paranoia-"+ endThis.name +"-concept-vsechno.png"
                    visible: false
                }
                */
            }

            Item{
                id: newTurnHolder
                anchors.fill: parent

                Text{
                    anchors.centerIn: parent
                    font {bold: true; italic: true; family: fontFace.name; capitalization: Font.AllUppercase; underline: true; pixelSize: parent.height * 0.2}
                    text: "New Turn"
                    color: "darkRed"
                }
            }

            Item{
                id: playersScan
                anchors.fill: parent

                property int number: 0

                visible: parent._state === "scanningPlayers"

                SequentialAnimation{
                    id: playersScanAnimation
                    PropertyAction{ target: playersScanRow; property: "visible"; value: "false"}
                    PropertyAction{ target: blocker; property: "opacity"; value: "0"}
                    PropertyAction{ target: blocker; property: "visible"; value: "true"}
                    PropertyAction{ target: blocker; property: "color"; value: "black"}
                    NumberAnimation{ target: blocker; property: "opacity"; from: 0; to: 1; duration: 1500}
                    PauseAnimation{ duration: 1000}
                    PropertyAnimation{ target: blocker; property: "color"; to: "white"; duration: 500; easing.type: Easing.OutInQuint}
                    PropertyAction{ target: playersScanRow; property: "visible"; value: "true"}
                    PropertyAnimation{ target: blocker; property: "color"; to: Qt.rgba(0, 0, 0, 0.8); duration: 500; easing.type: Easing.InOutQuint}
                }

                Row{
                    id: playersScanRow
                    anchors.centerIn: parent
                    spacing: 0.05                    

                    Repeater{
                        model: playersScan.number
                        delegate: Image{
                            id: myImage
                            width: app.width* 0.12; height: app.height* 0.3
                            anchors.verticalCenter: playersScanRow.verticalCenter
                            source: "../images/rooms/cards/badone.png"

                            MouseArea{anchors.fill: parent}
                        }
                    }
                }
            }

            Item{
                id: playerScan
                anchors.fill: parent

                visible: parent._state === "scanningPlayer"

                property variant items: []
                property variant blood: []

                Item{
                    id: bloodScanHolder

                    width: app.width*0.45
                    height: app.height*0.25
                    anchors.horizontalCenter: parent.horizontalCenter
                    y: app.height* 0.2

                    Repeater{
                        model: playerScan.blood.length
                        delegate: CardInHand{
                            id: myItem1
                            target: bloodScanHolder
                            cards: playerScan.blood

                            name: cards[index]
                            number: 0

                            MouseArea{
                                anchors.fill: parent
                                hoverEnabled: true
                                onEntered: {
                                    myItem1.z= 1
                                    myItem1.scale= 1
                                    myItem1._radius= target.width*1.05
                                }
                                onExited: {
                                    myItem1.z= 0
                                    myItem1.scale= 1 - 0.08* Math.abs(offset)
                                    myItem1._radius= Qt.binding(function(){return target.width})
                                }
                            }
                        }
                    }
                }

                Item{
                    id: itemScanHolder

                    width: app.width*0.45
                    height: app.height*0.25
                    anchors.horizontalCenter: parent.horizontalCenter
                    y: app.height* 0.4

                    Repeater{
                        model: playerScan.items.length
                        delegate: CardInHand{
                            id: myItem2
                            target: itemScanHolder
                            cards: playerScan.items

                            name: cards[index][0]
                            number: cards[index][1]

                            MouseArea{
                                anchors.fill: parent
                                hoverEnabled: true
                                onEntered: {
                                    myItem2.z= 1
                                    myItem2.scale= 1
                                    myItem2._radius= target.width*1.05
                                }
                                onExited: {
                                    myItem2.z= 0
                                    myItem2.scale= 1 - 0.08* Math.abs(offset)
                                    myItem2._radius= Qt.binding(function(){return target.width})
                                }
                            }
                        }
                    }
                }
            }

            Item{
                id: directionPicker

                visible: {
                    if(parent._state === "pickingAction" && (focusAction.imageSrc === "grenadeico" || (focusAction.imageSrc === "gunico" && app.cardsOnBoard[app.me][3]))) {
                        return true
                    }
                    else {
                        return false
                    }
                }

                width: parent.width*0.2; height: width
                x: parent.width*0.75; y: parent.height*0.4

                property variant selected: [0, 0]
                property variant hovered: []

                DirectionComponent{
                    id: midDirection
                    width: directionPicker.width*0.3; height: width
                    anchors.centerIn: parent
                    move: [0, 0]
                    img: "centerico"
                }

                DirectionComponent{
                    id: leftDirection
                    rotation: 180
                    anchors {right: midDirection.left; verticalCenter: midDirection.verticalCenter}
                    move: [0, -1]
                }
                DirectionComponent{
                    id: rightDirection
                    rotation: 0
                    anchors {left: midDirection.right; verticalCenter: midDirection.verticalCenter}
                    move: [0, 1]
                }
                DirectionComponent{
                    id: topDirection
                    rotation: -90
                    anchors {bottom: midDirection.top; horizontalCenter: midDirection.horizontalCenter}
                    move: [-1, 0]
                }
                DirectionComponent{
                    id: bottomDirection
                    rotation: 90
                    anchors {top: midDirection.bottom; horizontalCenter: midDirection.horizontalCenter}
                    move: [1, 0]
                }


            }
            Rectangle{
                id: coverPicker
                visible: parent._state === "cover"
                anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width*0.2; height: parent.height*0.35
                y: parent.height*0.35- height/2
                color: "grey"
                border {width: 10; color: "white"}
                radius: width*0.1

                property int points: 0
                property variant dmgClone: [0, 0]
                property variant dmgPlayer: [0, 0]
                property int attacker: 0

                signal close
                signal setUp(int player, int humanT, int dmg)

                onClose: {
                    parent._state = ""
                    parent.visible= false
                    dangerAnimation.stop()
                    parent.color= "#b3000000"
                }
                onSetUp: {
                    coverTimer.time = 5
                    if(coverTimer.running){
                        if(!humanT) {
                            dmgClone[0] += dmg
                            dmgCloneChanged()
                        }
                        else{
                            dmgPlayer[0] += dmg
                            dmgPlayerChanged()
                        }
                    }
                    else{
                        dmgClone = [0, 0]
                        dmgPlayer = [0, 0]
                        if(!humanT) {
                            dmgClone[0] = dmg
                        }
                        else{
                            dmgPlayer[0] = dmg
                        }

                        dmgCloneChanged()
                        dmgPlayerChanged()
                        attacker= player
                        //Kolikrát se můžu krýt
                        for(var i=0; i< app.cardsInHand.length; i++){if(app.cardsInHand[i][0] === "Vest"){ points = app.cardsInHand[i][1]; break }}
                        coverTimer.start()
                    }
                }

                Timer {
                    id: coverTimer
                    property int time: 5
                    interval: 1000; running: false; repeat: true
                    onTriggered: {
                        if(!time){
                            coverPicker.close()
                            coverTimer.stop()
                        }
                        else{
                            time -= 1
                        }
                    }
                }

                Rectangle{
                    anchors.verticalCenter: parent.top
                    x: parent.width*0.9 - width
                    width: parent.width*0.2; height: width
                    radius: width/2
                    border {width: 5; color: "white"}
                    color: "darkRed"

                    Text{
                        anchors.centerIn: parent
                        font {bold: true; family: fontFace.name; pixelSize: parent.width*0.6}
                        color: "white"
                        text: coverTimer.time
                    }
                }

                Rectangle{
                    anchors.verticalCenter: parent.top
                    x: parent.width*0.1
                    width: parent.width*0.4; height: parent.height*0.22
                    radius: height*0.3
                    border {width: 5; color: "white"}

                    gradient: Gradient {
                        GradientStop {
                            position: 0
                            color: if(coverPicker.attacker > -1){app._colors[app.avatars[coverPicker.attacker]]} else {"cyan"}
                        }

                        GradientStop {
                            position: 1
                            color: "black"
                        }
                    }

                    Image{
                        anchors.verticalCenter: parent.verticalCenter
                        width: parent.width*0.3; height: parent.height* 0.7
                        x: parent.width*0.15
                        source: {
                            if(coverPicker.attacker > -1){return "../images/avatars/heads/clone"+coverPicker.attacker+".png"}
                            else {return "../images/avatars/Parasites/parasite.png"}
                        }
                    }
                    Rectangle{
                        visible: coverPicker.attacker !== -1
                        anchors.verticalCenter: parent.verticalCenter
                        width: parent.width*0.3; height: parent.height* 0.6
                        x: parent.width*0.55
                        border {width: 2; color: "white"}
                        color: "firebrick"
                        radius: height*0.1

                        Image{
                            anchors.centerIn: parent
                            width: parent.width*0.8; height: width
                            source: "../images/rooms/icons/gunico.png"
                        }
                    }
                }

                Rectangle{
                    anchors {verticalCenter: parent.bottom; horizontalCenter: parent.horizontalCenter}
                    width: parent.width*0.16; height: width
                    radius: width/2
                    border {width: 5; color: "white"}
                    color: "green"

                    Text{
                        anchors.centerIn: parent
                        font {bold: true; family: fontFace.name; pixelSize: parent.width*0.6}
                        color: "white"
                        text: coverPicker.points
                    }
                }

                Row{
                    id: coverCloneRow
                    anchors.horizontalCenter: coverCloneCol.horizontalCenter
                    width: parent.width * 0.4
                    y: parent.height * 0.15
                    spacing: width * 0.05
                    visible: if(parent.dmgClone[0]) {true} else {false}
                    Repeater{
                        model: app.hitPoints[app.me][0]
                        delegate: Image{
                            width: coverCloneRow.width*0.2; height: width
                            anchors.verticalCenter: coverCloneRow.verticalCenter
                            source: {
                                var name
                                var hp = app.hitPoints[app.me][0]
                                if((hp - index) > coverPicker.dmgClone[0]){name = "Heart00"}
                                else if((hp - index) > coverPicker.dmgClone[0] - coverPicker.dmgClone[1]) {name = "HeartG"}
                                else {name = "HeartO"}

                                return ("../images/useful/"+name+".png")
                            }
                        }
                    }
                }
                Row{
                    id: coverPlayerRow
                    anchors.horizontalCenter: coverPlayerCol.horizontalCenter
                    width: parent.width * 0.4; height: parent.height * 0.1
                    y: parent.height * 0.15
                    spacing: width * 0.05
                    visible: if(parent.dmgPlayer[0]) {true} else {false}
                    Repeater{
                        model: app.hitPoints[app.me][1]
                        delegate: Image{
                            width: coverPlayerRow.width*0.2; height: width
                            anchors.verticalCenter: coverPlayerRow.verticalCenter
                            source: {
                                var name
                                var hp = app.hitPoints[app.me][1]
                                if((hp - index) > coverPicker.dmgPlayer[0]){name = "Heart00"}
                                else if((hp - index) > (coverPicker.dmgPlayer[0] - coverPicker.dmgPlayer[1])) {name = "HeartG"}
                                else {name = "HeartO"}

                                return ("../images/useful/"+name+".png")
                            }
                        }
                    }
                }


                Column{
                    id: coverCloneCol
                    visible: coverPicker.dmgClone[0]
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width*0.35; height: parent.height*0.42
                    x: parent.width*0.1
                    spacing: height*0.1

                    Rectangle{
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: parent.width*0.7; height: parent.height*0.7
                        color: app._colors[me.avatar]
                        radius: 5
                        border {width: 5; color: Qt.lighter("grey")}

                        Image {
                            width: parent.width*0.8; height: parent.height*0.8
                            source: "../images/avatars/heads/clone" + me.avatar + ".png"
                            anchors.centerIn: parent
                        }
                    }

                    Item{
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: parent.width*0.7; height: width
                        opacity: 0.5

                        Image{
                            width: parent.width*0.8; height: parent.height*0.8
                            source: "../images/rooms/icons/coverico.png"
                            anchors.centerIn: parent
                        }
                        MouseArea{
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: {
                                if(coverPicker.dmgClone[0] === coverPicker.dmgClone[1] || !coverPicker.points){ return }
                                coverPicker.points -= 1
                                coverPicker.dmgClone[1]+= 1
                                coverPicker.dmgCloneChanged()
                                app._cover(0)
                            }
                            onEntered: parent.opacity= 0.9
                            onExited: parent.opacity= 0.5
                        }

                    }
                }
                Column{
                    id: coverPlayerCol
                    visible: coverPicker.dmgPlayer[0]
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width*0.35; height: parent.height*0.42
                    x: parent.width*0.9 - width
                    spacing: height*0.1

                    Rectangle{
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: parent.width*0.7; height: parent.height*0.7
                        color: app._colors[me.avatar]
                        radius: 5
                        border {width: 5; color: Qt.lighter("grey")}

                        Image {
                            width: parent.width*0.8; height: parent.height*0.8
                            source: "../images/avatars/heads/player" + me.avatar + ".png"
                            anchors.centerIn: parent
                        }
                    }

                    Item{
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: parent.width*0.7; height: width
                        opacity: 0.5

                        Image{
                            width: parent.width*0.8; height: parent.height*0.8
                            source: "../images/rooms/icons/coverico.png"
                            anchors.centerIn: parent
                        }
                        MouseArea{
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: {
                                if(coverPicker.dmgPlayer[0] === coverPicker.dmgPlayer[1] || !coverPicker.points){ return }
                                coverPicker.points -= 1
                                coverPicker.dmgPlayer[1]+= 1
                                coverPicker.dmgPlayerChanged()
                                app._cover(1)
                            }
                            onEntered: parent.opacity= 0.9
                            onExited: parent.opacity= 0.5
                        }

                    }
                }
                MouseArea{ anchors.fill: parent; z: -1 }
            }

            Rectangle{
                id: healPicker
                visible: parent._state === "healingPlayer"
                anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width*0.2; height: parent.height*0.3
                y: parent.height*0.35- height/2
                color: "grey"
                border {width: 10; color: "white"}
                radius: width*0.1

                property int points: 2
                property variant hitPoints: [[], []]
                property int hospital

                signal close
                signal setUp(int clone)

                onClose: {
                    parent.state= ""
                    parent.visible= false
                }
                onSetUp: {
                    var HP= [[], []]
                    var i
                    for(i=0; i< app.hitPoints[app.me][0]; i++){HP[0].push(1)}
                    for(i=0; i< app.hitPoints[app.me][1]; i++){HP[1].push(1)}

                    hospital= clone
                    hitPoints= HP
                    points= 2
                    hitPointsChanged()
                }

                Timer {
                    id: healPlayerTimer
                    interval: 1500; running: false; repeat: false
                    onTriggered: {
                        var i
                        var a= 0
                        var b= 0                        
                        for(i= 0; i< healPicker.hitPoints[0].length; i++){if(healPicker.hitPoints[0][i] === 2){a += 1}}
                        for(i= 0; i< healPicker.hitPoints[1].length; i++){if(healPicker.hitPoints[1][i] === 2){b += 1}}
                        healPicker.close()

                        if(healPicker.hospital > -1){app._heal(healPicker.hospital, (a ? a : b))}
                        else {app._healPlayer(a, b)}
                    }
                }

                Rectangle{
                    anchors {verticalCenter: parent.bottom; horizontalCenter: parent.horizontalCenter}
                    width: parent.width*0.16; height: width
                    radius: width/2
                    border {width: 5; color: "white"}
                    color: "green"

                    Text{
                        anchors.centerIn: parent
                        font {bold: true; family: fontFace.name; pixelSize: parent.width*0.6}
                        color: "white"
                        text: healPicker.points
                    }
                }


                Row{
                    id: healCloneRow
                    anchors.horizontalCenter: healCloneCol.horizontalCenter
                    width: parent.width * 0.4
                    y: parent.height * 0.1
                    spacing: width * 0.05
                    visible: healCloneCol.visible
                    Repeater{
                        model: healPicker.hitPoints[0].length
                        delegate: Image{
                            width: healCloneRow.width*0.2; height: width
                            anchors.verticalCenter: healCloneRow.verticalCenter
                            source: {
                                var name
                                if(healPicker.hitPoints[0][index] === 1){ name = "Heart01"}
                                else if(healPicker.hitPoints[0][index] === 2){ name = "HeartG"}

                                return ("../images/useful/"+name+".png")
                            }
                        }
                    }
                }
                Row{
                    id: healPlayerRow
                    anchors.horizontalCenter: healPlayerCol.horizontalCenter
                    width: parent.width * 0.4; height: parent.height * 0.1
                    y: parent.height * 0.1
                    spacing: width * 0.05
                    visible: healPlayerCol.visible
                    Repeater{
                        model: healPicker.hitPoints[1].length
                        delegate: Image{
                            width: healPlayerRow.width*0.2; height: width
                            anchors.verticalCenter: healPlayerRow.verticalCenter
                            source: {
                                var name
                                if(healPicker.hitPoints[1][index] === 1){ name = "Heart00"}
                                else if(healPicker.hitPoints[1][index] === 2){ name = "HeartG"}

                                return ("../images/useful/"+name+".png")
                            }
                        }
                    }
                }


                Column{
                    id: healCloneCol
                    visible: ((healPicker.hospital === 1) ? false : (0 < app.hitPoints[app.me][0] < 4))
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width*0.35; height: parent.height*0.5
                    x: parent.width*0.1
                    spacing: height*0.1

                    Rectangle{
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: parent.width*0.6; height: parent.height*0.6
                        color: app._colors[me.avatar]
                        radius: 5
                        border {width: 5; color: Qt.lighter("grey")}

                        Image {
                            width: parent.width*0.8; height: parent.height*0.8
                            source: "../images/avatars/heads/clone" + me.avatar + ".png"
                            anchors.centerIn: parent
                        }
                    }

                    Item{
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: parent.width*0.5; height: width
                        opacity: 0.5

                        Image{
                            width: parent.width*0.8; height: parent.height*0.8
                            source: "../images/rooms/icons/plusico.png"
                            anchors.centerIn: parent
                        }
                        MouseArea{
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: {
                                if(healPicker.hitPoints[0].length === 4 || !healPicker.points){ return }
                                healPicker.points -= 1
                                healPicker.hitPoints[0].push(2)
                                healPicker.hitPointsChanged()
                                if(!healPicker.points || (healPicker.hitPoints[0].length === 4 && (healPicker.hitPoints[1].length === 4 || healPicker.hospital === 0)) ){
                                    healPlayerTimer.start()
                                }
                            }
                            onEntered: parent.opacity= 0.9
                            onExited: parent.opacity= 0.5
                        }

                    }
                }
                Column{
                    id: healPlayerCol
                    visible: ((healPicker.hospital === 0) ? false : (0 < app.hitPoints[app.me][1] < 4))
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width*0.35; height: parent.height*0.5
                    x: parent.width*0.9 - width
                    spacing: height*0.1

                    Rectangle{
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: parent.width*0.6; height: parent.height*0.6
                        color: app._colors[me.avatar]
                        radius: 5
                        border {width: 5; color: Qt.lighter("grey")}

                        Image {
                            width: parent.width*0.8; height: parent.height*0.8
                            source: "../images/avatars/heads/player" + me.avatar + ".png"
                            anchors.centerIn: parent
                        }
                    }

                    Item{
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: parent.width*0.5; height: width
                        opacity: 0.5

                        Image{
                            width: parent.width*0.8; height: parent.height*0.8
                            source: "../images/rooms/icons/plusico.png"
                            anchors.centerIn: parent
                        }
                        MouseArea{
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: {
                                if(healPicker.hitPoints[1].length === 4 || !healPicker.points){ return }
                                healPicker.points -= 1
                                healPicker.hitPoints[1].push(2)
                                healPicker.hitPointsChanged()
                                if(!healPicker.points || (healPicker.hitPoints[1].length === 4 && (healPicker.hitPoints[0].length === 4 || healPicker.hospital === 1)) ){
                                    healPlayerTimer.start()
                                }
                            }
                            onEntered: parent.opacity= 0.9
                            onExited: parent.opacity= 0.5
                        }

                    }
                }
                MouseArea{ anchors.fill: parent; z: -1 }
            }


            Rectangle{
                id: playerPicker
                width: height; height: parent.height*0.5
                radius: height/2
                color: "#00000000"
                border.width: 5; border.color: "green"
                visible: parent._state === "pickingAction" || parent._state === "pickingCard"
                anchors {horizontalCenter: parent.horizontalCenter}
                y: parent.height*0.35- height/2

                property int player
                property int human
                property int meHuman
                property int selected   //Určuje která ikonka je aktivní
                property variant showActions: [false, false, false, false]
                property string currentRoom
                property int parasite

                signal reset
                onReset: {
                    showActionsChanged()
                    actionSwitcher.state= "default"
                    directionPicker.selected= [0, 0]
                    player= app.meeting[0][2]
                    if (app.meeting.length > 1){
                        parasite = -1
                    }
                    else{
                        parasite = 2
                    }
                    if(app.meeting[0][0]){
                        human= 0
                        selected = 0
                    }
                    else {
                        human= 1
                        selected= 1
                    }
                }

                Component{
                    id: pickPlayerComponent
                     Rectangle{
                        id: rect
                        visible: if(app.meeting[ind][human]){true} else {false}
                        width: playerPicker.width*0.15; height: width
                        border {width: 3; color: app._colors[avatar]}
                        color: {
                            if(playerPicker.selected===index){
                                scale= 1.4
                                return Qt.darker(Qt.darker(app._colors[avatar]))
                            }
                            if(hover) {scale= 1; return Qt.lighter(app._colors[avatar])}
                            else{scale= 1; return Qt.darker(app._colors[avatar])}
                        }
                        radius: width/3
                        y: {playerPicker.width*0.5 + y1 - height/2}
                        x: {playerPicker.width*0.5 + x1 - width/2}

                        property bool hover: false
                        property int ind: index% (app.meeting.length- 1)
                        property int player: app.meeting[ind][2]
                        property int human: if(index > (app.meeting.length - 2)){ 1 } else { 0 }
                        property int avatar: {app.avatars[player]}
                        property double angle: {
                            if(human){
                                (Math.PI*2/app.meeting.length)* (ind) -0.2
                            }
                            else{
                                (Math.PI*2/app.meeting.length)* (ind) +0.2
                            }
                        }
                        property int y1: Math.sin(angle)*(playerPicker.width*0.5)
                        property int x1: Math.cos(angle)*(playerPicker.width*0.5)

                        Behavior on scale {
                            PropertyAnimation {
                                easing.type: Easing.OutElastic;
                                easing.amplitude: 10.0;
                                easing.period: 2.0;
                                target: rect;
                                property: "scale";
                                duration: 300
                            }
                        }


                        Image{
                            id: im
                            width: parent.width*0.6; height: parent.height*0.8
                            anchors.centerIn: parent
                            source: if(human){"../images/avatars/heads/player"+ parent.avatar +".png"} else {"../images/avatars/heads/clone"+ parent.avatar+".png"}}

                        MouseArea{
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: {
                                playerPicker.player= parent.player;
                                playerPicker.human= parent.human;
                                playerPicker.selected= index;
                                playerPicker.parasite= -1;
                            }
                            onEntered: {
                                rect.hover= true
                            }
                            onExited: {
                                rect.hover= false
                            }
                        }
                    }
                }

                Component{
                    id: pickParasiteComponent
                     Rectangle{
                        id: rect
                        visible: if(app.meeting[app.meeting.length - 1][type]){true} else{false}
                        width: playerPicker.width*0.15; height: width
                        border {width: 3; color: "grey"}
                        scale: {if(playerPicker.selected === ind){return 1.4} else {return 1}}
                        radius: width/3
                        y: {playerPicker.width*0.5 + y1 - height/2}
                        x: {playerPicker.width*0.5 + x1 - width/2}

                        property int type: index
                        property int ind: app.meeting.length*2 -1 + type

                        property bool hover: false
                        property double angle: {
                            var _angle= (Math.PI*2/app.meeting.length)* (app.meeting.length -1)
                            if(type === 0){return _angle +0.2}
                            if(type === 1){return _angle +0.0}
                            if(type === 2){return _angle -0.2}
                        }

                        property int y1: Math.sin(angle)*(playerPicker.width*0.5)
                        property int x1: Math.cos(angle)*(playerPicker.width*0.5)

                        Behavior on scale {
                            PropertyAnimation {
                                easing.type: Easing.OutElastic;
                                easing.amplitude: 10.0;
                                easing.period: 2.0;
                                target: rect;
                                property: "scale";
                                duration: 300
                            }
                        }

                        gradient: Gradient {
                            GradientStop {
                                position: 0
                                color: {
                                    if(rect.type === 2) {return "black"}
                                    else {return "white"}
                                }
                            }

                            GradientStop {
                                position: 1
                                color: {
                                    if(rect.type === 0) {return "white"}
                                    else {return "black"}
                                }
                            }
                        }

                        Text{
                            font {bold: true; family: fontFace.name; pixelSize: parent.width*0.4}
                            anchors {bottom: parent.bottom; right: parent.right}
                            color: "green"
                            text: app.meeting[app.meeting.length - 1][rect.type]
                        }

                        Image{
                            id: im
                            width: parent.width*0.6; height: parent.height*0.8
                            anchors.centerIn: parent
                            source: "../images/avatars/Parasites/parasite.png"
                        }

                        MouseArea{
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: {
                                playerPicker.selected= parent.ind;
                                playerPicker.parasite= rect.type;
                            }
                            onEntered: {
                                rect.hover= true
                            }
                            onExited: {
                                rect.hover= false
                            }
                        }
                    }
                }

                Repeater{
                    model: if(app.meeting.length){return (app.meeting.length - 1)*2} else {return 0}
                    delegate: pickPlayerComponent
                }
                Repeater{
                    model: if(app.meeting.length && actionSwitcher.state !== "meeting"){return 3} else {return 0}
                    delegate: pickParasiteComponent
                }

                Item {
                    id: pickAction
                    visible: blocker._state !== "pickingCard"
                    width: parent.width*0.4; height: width
                    anchors.centerIn: parent

                    Rectangle{
                        id: actionSwitcher
                        state: "default"
                        states:[
                            State{
                                name: "default"
                                PropertyChanges{target: aSImage; source: "../images/rooms/icons/playersico.png"}
                                PropertyChanges{target: actionSwitcher; color: "blue"}
                            },
                            State{
                                name: "Terminal"
                                PropertyChanges{target: aSImage; source: "../images/rooms/icons/roomico.png"}
                                PropertyChanges{target: actionSwitcher; color: "green"}
                                PropertyChanges{target: topRect; src: "searchico"; show: true;
                                    onChoosed: app._drawCard(playerPicker.meHuman, playerPicker.player, playerPicker.human, playerPicker.parasite)
                                }
                                PropertyChanges{target: bottomRect; show: false}
                                PropertyChanges{target: rightRect; src: "doorico"; onChoosed: app._openDoors(playerPicker.meHuman); show: true}
                                PropertyChanges{target: leftRect; src: "fingerscanico"; onChoosed: app._scan(playerPicker.meHuman); show: true}
                            },
                            State{
                                name: "Hospital"
                                PropertyChanges{target: aSImage; source: "../images/rooms/icons/roomico.png"}
                                PropertyChanges{target: actionSwitcher; color: "green"}
                                PropertyChanges{target: topRect; src: "searchico"; show: true;
                                    onChoosed: app._drawCard(playerPicker.meHuman, playerPicker.player, playerPicker.human, playerPicker.parasite)
                                }
                                PropertyChanges{target: bottomRect; show: false}
                                PropertyChanges{target: rightRect; src: "healico"; onChoosed: app.tryHeal(playerPicker.meHuman); show: true}
                                PropertyChanges{target: leftRect; show: false}
                            },
                            State{
                                name: "Nest"
                                PropertyChanges{target: aSImage; source: "../images/rooms/icons/roomico.png"}
                                PropertyChanges{target: actionSwitcher; color: "green"}
                                PropertyChanges{target: topRect; show: false;
                                    onChoosed: app._drawCard(playerPicker.meHuman, playerPicker.player, playerPicker.human, playerPicker.parasite)
                                }
                                PropertyChanges{target: bottomRect; show: false}
                                PropertyChanges{target: rightRect; src: "burnico"; onChoosed: app._burn(); show: true}
                                PropertyChanges{target: leftRect; show: false}
                            },
                            State{
                                name: "Nothing"
                                PropertyChanges{target: aSImage; source: "../images/rooms/icons/roomico.png"}
                                PropertyChanges{target: actionSwitcher; color: "green"}
                                PropertyChanges{target: topRect; show: false;
                                    onChoosed: app._drawCard(playerPicker.meHuman, playerPicker.player, playerPicker.human, playerPicker.parasite)
                                }
                                PropertyChanges{target: bottomRect; show: false}
                                PropertyChanges{target: rightRect; show: false}
                                PropertyChanges{target: leftRect; show: false}
                            },
                            State{
                                name: "Other"
                                PropertyChanges{target: aSImage; source: "../images/rooms/icons/roomico.png"}
                                PropertyChanges{target: actionSwitcher; color: "green"}
                                PropertyChanges{target: topRect; src: "searchico"; show: true;
                                    onChoosed: app._drawCard(playerPicker.meHuman, playerPicker.player, playerPicker.human, playerPicker.parasite)
                                }
                                PropertyChanges{target: bottomRect; show: false}
                                PropertyChanges{target: rightRect; show: false}
                                PropertyChanges{target: leftRect; show: false}
                            },
                            State{
                                name: "meeting"
                                PropertyChanges{target: actionSwitcher; visible: false}
                                PropertyChanges{target: topRect; src: "exchangeico"; show: true;
                                    onChoosed: blocker._state = "pickingCard"
                                }
                                StateChangeScript{
                                    script: {
                                        //bottomRect.src = (playerPicker.meHuman ? "knifeico" : "gunico")
                                    }
                                }
                                PropertyChanges{target: bottomRect; show: true;
                                    src: (playerPicker.meHuman ? "knifeico" : "gunico");
                                    onChoosed: {
                                        if(!playerPicker.meHuman){app._shoot(playerPicker.player, playerPicker.human, -1, [0, 0])}
                                        else {app._stab(playerPicker.player, playerPicker.human, -1)}
                                        blocker._state = ""
                                        blocker.visible = false
                                    }
                                }
                                PropertyChanges{target: rightRect; visible: false}
                                PropertyChanges{target: leftRect; visible: false}
                            }
                        ]

                        anchors.centerIn: parent
                        width: parent.width*0.5; height: width
                        radius: width/2
                        color: "#646464"
                        border.width: 6; border.color: "white"

                        Image{
                            id: aSImage
                            anchors.centerIn: parent
                            width: parent.width*0.55; height: width
                            source: ""
                        }
                        MouseArea{
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: {
                                if(actionSwitcher.state==="default"){
                                    if (playerPicker.currentRoom==="Terminal" || playerPicker.currentRoom==="Terminal2"){actionSwitcher.state= "Terminal"}
                                    else if (playerPicker.currentRoom==="FirstAid"){actionSwitcher.state= "Hospital"}
                                    else if (playerPicker.currentRoom==="Nest"){actionSwitcher.state= "Nest"}
                                    else if (playerPicker.currentRoom==="Reactor" || playerPicker.currentRoom==="Empty"){actionSwitcher.state= "Nothing"}
                                    else {actionSwitcher.state= "Other"}
                                }
                                else {actionSwitcher.state= "default"}
                            }

                            onEntered: parent.border.color= "orange"
                            onExited: parent.border.color= "white"
                        }
                    }

                    Rectangle {

                        anchors.fill: parent
                        radius: parent.width/4
                        color: "transparent"
                        border.width: 4; border.color: "white"


                        SideRect {
                            id: leftRect
                            anchors { verticalCenter: parent.verticalCenter; horizontalCenter: parent.left }
                            src: "knifeico"; show: (playerPicker.showActions[3] && app.human)
                            onChoosed: app._stab(playerPicker.player, playerPicker.human, playerPicker.parasite)
                        }

                        SideRect {
                            id: rightRect
                            anchors { verticalCenter: parent.verticalCenter; horizontalCenter: parent.right }
                            src: "gunico"; show: (playerPicker.showActions[1] && !app.human)
                            onChoosed: app._shoot(playerPicker.player, playerPicker.human, playerPicker.parasite, directionPicker.selected)

                        }

                        SideRect {
                            id: topRect
                            anchors { verticalCenter: parent.top; horizontalCenter: parent.horizontalCenter }
                            src: "palmscanico"; show: (playerPicker.showActions[0] && playerPicker.parasite === -1)
                            onChoosed: app._scanPlayer(playerPicker.meHuman, playerPicker.player, playerPicker.human)
                        }

                        SideRect {
                            id: bottomRect
                            anchors { verticalCenter: parent.bottom; horizontalCenter: parent.horizontalCenter }
                            src: "grenadeico"; show: playerPicker.showActions[2]
                            onChoosed: app._throwGrenade(playerPicker.meHuman, directionPicker.selected)
                        }


                        Rectangle {
                            id: focusAction

                            property string imageSrc: ""

                            width: parent.width*0.35; height: width
                            radius: 6
                            border.width: 4; border.color: "white"
                            color: "firebrick"


                            x: bottomRect.x; y: bottomRect.y

                            Behavior on x {
                                NumberAnimation { easing.type: Easing.OutElastic; easing.amplitude: 3.0; easing.period: 2.0; duration: 300 }
                            }


                            Behavior on y {
                                NumberAnimation { easing.type: Easing.OutElastic; easing.amplitude: 3.0; easing.period: 2.0; duration: 300 }
                            }

                            Image {
                                id: focusImage
                                source: if(focusAction.imageSrc){"../images/rooms/icons/"+focusAction.imageSrc+".png"} else{""}
                                anchors.centerIn: parent
                                width: parent.width*0.65; height: width

                                Behavior on source {
                                    SequentialAnimation {
                                        NumberAnimation { target: focusImage; property: "opacity"; to: 0; duration: 150 }
                                        NumberAnimation { target: focusImage; property: "opacity"; to: 1; duration: 150 }
                                    }
                                }
                            }
                        }
                    }
                }

                Item{
                    id: pickCard
                    visible: blocker._state === "pickingCard"

                    width: parent.width* 0.7; height: parent.height*0.45
                    anchors.centerIn: parent

                    property bool sent: false
                    property string cardImg: ""
                    property bool cardSet: false

                    signal changingCards()

                    Timer {
                        id: pickCardTimer
                        interval: 3000; running: false; repeat: false
                        onTriggered: {
                            blocker.visible= false
                            blocker._state = ""
                            hisCard.img= ""
                            pickCard.sent= false
                            pickCard.cardImg= ""
                            pickCard.cardSet= false
                        }
                    }

                    Rectangle{
                        id: myCard

                        anchors.right: parent.horizontalCenter; anchors.rightMargin: parent.width*0.05
                        width: parent.width*0.45; height: parent.height
                        radius: width*0.2
                        color: if(!pickCard.cardSet){return blocker.color} else {return "#80158a1c"}
                        border {width: 2; color: "white"}

                        Image{
                            anchors.centerIn: parent
                            width: parent.width*0.8; height: parent.height*0.8
                            source: if(pickCard.cardImg){return "../images/rooms/cards/"+pickCard.cardImg+".png"} else {return ""}
                        }
                    }
                    Rectangle{
                        id: hisCard

                        property string img: ""

                        anchors.left: parent.horizontalCenter; anchors.leftMargin: parent.width*0.05
                        width: parent.width*0.45; height: parent.height
                        radius: width*0.2
                        color: if(!img){return blocker.color} else {return "#80158a1c"}
                        border {width: 2; color: "white"}

                        Image{
                            anchors.centerIn: parent
                            width: parent.width*0.8; height: parent.height*0.8
                            source: if(hisCard.img){return "../images/rooms/cards/"+hisCard.img+".png"} else {return ""}
                        }
                    }

                    Rectangle{

                        anchors {horizontalCenter: parent.horizontalCenter; verticalCenter: myCard.bottom}

                        width: parent.width*0.2; height: width
                        color: if (pickCard.sent){return "green"} else {return "grey"}
                        radius: width/2
                        border {width: 2; color: "white"}

                        Text{
                            anchors.centerIn: parent
                            text: "Okay"
                            font {bold: true; family: fontFace.name;  pixelSize: parent.width*0.25}
                            color: "orange"
                        }

                        MouseArea{
                            anchors.fill: parent
                            onClicked: {
                                if(!pickCard.sent && pickCard.cardSet){
                                    pickCard.sent= true
                                    app._changeCards(pickCard.cardImg, playerPicker.meHuman, playerPicker.player, playerPicker.human)

                                }
                            }
                        }
                    }
                }
            }
        }

        Rectangle {
            id: bar
            width: parent.width
            height: parent.height*0.25
            color: "#00000000"
            border.width: 0
            anchors.bottomMargin: 0
            border.color: "#00000000"
            anchors.bottom: parent.bottom



            Item{
                id: me
                anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter
                width: parent.width*0.25
                height: app.height*0.25

                property int avatar: app.avatars[app.me]

                Image{
                    source: "../images/useful/PlayerBoard.png"
                    anchors.fill: parent
                }

                Grid {
                    id: meCardsUsed
                    x: parent.width*0.28; y: parent.height*0.18
                    columns: 2
                    spacing: 10

                    Repeater {
                        model: ListModel {
                            ListElement {
                                name: 0
                                image: "Knife"
                            }

                            ListElement {
                                name: 1
                                image: "Card"
                            }

                            ListElement {
                                name: 2
                                image: "Riffle"
                            }

                            ListElement {
                                name: 3
                                image: "Scope"
                            }
                        }

                        delegate: Rectangle {
                            id: rect
                            width: me.width*0.12; height: width
                            radius: width*0.1
                            color: "#4c000000"
                            border {width: 2; color: "black"}
                            
                            state: {if(app.cardsOnBoard[app.me][index]){return "active"} else {return "inactive"}}
                            states: [
                                State{
                                    name: "active"
                                    PropertyChanges{target: img; source: "../images/rooms/icons/"+image+".png"}
                                    PropertyChanges{target: rect; color: "#4c13d533"}
                                },
                                State {
                                    name: "inactive"
                                    PropertyChanges{target: img; source: "../images/rooms/icons/"+image+"n.png"}
                                    PropertyChanges{target: rect; color: "#4c000000"}
                                }
                            ]

                            Image{
                                id: img
                                width: parent.width*0.8; height: width
                                source: ""
                                anchors.centerIn: parent
                            }
                        }
                    }
                }

                Column{
                    x: parent.width*0.07; y: parent.height*0.15
                    width: parent.width*0.18; height: parent.height*0.8
                    spacing: 10

                    MeHead{
                        id: mePlayer
                        human: 1
                        visible: app.hitPoints[app.me][1] > 0
                    }
                    MeHead{
                        id: meClone
                        human: 0
                        visible: app.hitPoints[app.me][0] > 0
                    }
                }

                Rectangle{
                    id: meBlood
                    width: parent.width*0.35; height: parent.height*0.8
                    x: parent.width*0.58; y: parent.height*0.1
                    color: bar.color
                    border.width: 0; border.color: "black"
                    radius:width/5


                    Column{
                        id: meBloodColumn
                        anchors.centerIn: parent
                        width: parent.width*0.1; height: parent.height*0.9
                        spacing: 5
                        rotation: 180
                        visible: false

                        Repeater{
                            model: app.blood.length

                            delegate: Rectangle{
                                id: rect2

                                property int bloodIndex: app.blood[index]

                                anchors.horizontalCenter: meBloodColumn.horizontalCenter
                                width: meBloodColumn.width*0.8; height: meBloodColumn.height/app.blood.length - 5
                                border {width: 0; color: "black"}
                                radius: width*0.15                              
                                color: Qt.darker(app._colors[app.avatars[bloodIndex]])

                                LinearGradient {
                                    source: rect2
                                    anchors.fill: parent
                                    start: Qt.point(0, 0)
                                    end: Qt.point(rect2.width, 0)
                                    gradient: Gradient {
                                        GradientStop { position: 0.0; color: Qt.lighter(rect2.color)}
                                        GradientStop { position: 0.4; color: Qt.darker(rect2.color)}
                                        GradientStop { position: 1.0; color: (rect2.color)}
                                    }
                                }
                            }
                        }
                    }
                    Column{
                        id: meBloodColumn1
                        anchors.centerIn: parent
                        width: parent.width*0.5; height: parent.height*0.8
                        spacing: 5
                        opacity: 0
                        Repeater{
                            model: app.blood.length

                            delegate: Rectangle{
                                id: rect1

                                property int bloodIndex: app.blood[index]
                                property string name: "Blood" + app.avatars[bloodIndex]

                                anchors.horizontalCenter: meBloodColumn1.horizontalCenter
                                width: meBloodColumn1.width*0.8; height: meBloodColumn1.height/app.blood.length - 5
                                radius: width*0.15

                                MouseArea{
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: {
                                        if(blocker._state === "pickingCard" && !pickCard.sent){
                                            if((app.me === rect1.bloodIndex && app.corrupted) || (app.me !== rect1.bloodIndex && !app.cardsInHand.length)){
                                            pickCard.cardImg= name; pickCard.cardSet= true}
                                        }
                                    }
                                    onEntered: {
                                        if(blocker._state === "pickingCard" && !pickCard.cardSet){pickCard.cardImg= name}
                                    }
                                    onExited: {
                                        if(blocker._state === "pickingCard" && !pickCard.cardSet){pickCard.cardImg= ""}
                                    }
                                }
                            }
                        }
                    }
                    Image{
                        id: meBloodImage
                        anchors.fill: parent
                        source: "../images/useful/blood2.png"
                        opacity: 0.9
                    }

                    OpacityMask {
                        anchors.centerIn: parent
                        width: parent.width*0.5; height: parent.height*0.8
                        source: meBloodColumn
                        maskSource: meBloodImage
                    }
                }

                Row {
                    id: meHPPlayer
                    x: parent.width*0.28; y: parent.height*0.7
                    height: parent.height*0.15

                    Repeater{
                        model: app.hitPoints[app.me][1]
                        Image{
                            width: height; height: meHPPlayer.height
                            source: "../images/useful/Heart00.png"
                        }
                    }
                }
                Row{
                    id: meHPClone
                    x: parent.width*0.3; y: parent.height*0.75
                    height: parent.height*0.15
                    Repeater{
                        model: app.hitPoints[app.me][0]
                        Image{
                            width: height; height: meHPClone.height
                            source: "../images/useful/Heart01.png"
                        }
                    }
                }

                Item{
                    id: meAmmo

                    property int ammo: app.ammos[app.me]

                    width: me.height * 0.18; height: me.height * 0.2
                    x: me.width - width*1.55; y: me.height - height*1.5

                    Image{
                        source: "../images/rooms/icons/ammo.png"
                        anchors.fill: parent
                    }

                    Text{
                        anchors.centerIn: parent
                        font {bold: true; family: fontFace.name; pixelSize: parent.height * 0.7}
                        color: "#ccffffff"
                        text: parent.ammo
                    }
                }

                MouseArea{
                    anchors.fill: parent
                    z: -1
                }
            }

        Item {
            id: meCardsInHandHolder
            width: parent.width*0.45
            height: app.height*0.25
            anchors.centerIn: parent
            z: 1

            Rectangle{
                width: meCardsInHandHolder.width*2
                height: width
                x: parent.width*0.5 - width/2
                y: width*0.05

                radius: width/2

                visible: false

                border {width: 5; color: "green"}
                color: bar.color
            }


            Image{
                id: ciHimage
                anchors.fill: parent
                source: "../images/useful/CardHolder.png"
            }

            Repeater{
                model: app.cardsInHand.length
                delegate: CardInHand{
                    id: myItem
                    target: meCardsInHandHolder
                    cards: app.cardsInHand

                    name: cards[index][0]
                    number: cards[index][1]

                }
            }

        }

        Item {
            id: actionsHolder
            width: parent.width*0.27
            height: app.height*0.24
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right


            Image{
                source: "../images/useful/ActionLog.png"
                anchors.fill: parent
            }

            ListView {
                id: actionsView
                anchors.centerIn: parent
                width: parent.width*0.93; height: parent.height
                keyNavigationWraps: false
                spacing: 10
                orientation: ListView.Horizontal
                flickableDirection: Flickable.HorizontalFlick
                clip: true

                signal newItem()

                onNewItem: incrementCurrentIndex()

                add: Transition {
                        NumberAnimation { properties: "x,y"; from: 100; duration: 1000 }
                    }

                delegate: ShootAction{
                    name: _name
                    player1: _player1
                    player2: _player2
                    human1: _human1
                    human2: _human2
                    src: _img
                    parasite: _paras
                    demage: _demage
                }


                model: actionsModel

                ListModel{id: actionsModel}
            }
        }
        }
    }
}

