__author__= """
░░░░███████ ]▄▄▄▄▄▄▄▄
▂▄▅█████████▅▄▃▂
Il███████████████████].
  ◥⊙▲⊙▲⊙▲⊙▲⊙▲⊙▲⊙◤.."""

from PyQt5.QtCore import pyqtProperty, QRectF, QUrl, QObject, pyqtSignal, pyqtSlot, QVariant, QTimer, QThread, QEvent
from PyQt5.QtGui import QColor, QGuiApplication, QPainter, QPen
from PyQt5.QtQml import qmlRegisterType
from PyQt5.QtQuick import QQuickItem, QQuickView
from PyQt5 import QtNetwork as QN
from PyQt5 import QtCore as QC


from multiprocessing import Process, Manager, freeze_support
import pyaudio
import numpy as np
import wave
import time
import win_unicode_console

from store import Buffer
import server as S
import client as C
import game

win_unicode_console.enable()

class Sound(QObject):

    sendVoice = pyqtSignal(bytes, int)


    WIDTH = 2
    CHANNELS = 2
    RATE = 44100

    MAX_INC = 255
    MAX_VOICE = 10

    def __init__(self, parent = None):
        super(Sound, self).__init__(parent)
        self.voiceStreams= (Buffer(), Buffer(), Buffer(), Buffer(), Buffer(), Buffer())     #6x pro šest hráčů
        self.musicStreams = [wave.open("Music\Paranoia.wav", "rb"), wave.open("Music\RightBehindYou.wav", "rb"), wave.open("Music\ParanormalActivity.wav", "rb")]
        self.effectStreams= []

        self.vVolume= 1
        self.mVolume= 1
        self.eVolume= 1

        self.voip = None

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format = self.p.get_format_from_width(Sound.WIDTH),
                        channels = Sound.CHANNELS,
                        rate = Sound.RATE,
                        input = True,
                        output = True,
                        #stream_callback = self.callback
                        )


        self.nextSample = ""
        self.lastSample = ""

        self.stream.start_stream()

    def addMusic(self, name):
        self.musicStreams.append(wave.open(name, "rb"))

    def addVoice(self, player, increment, voice):
        """
        :param player: od jakého hráče
        :param increment: kolikátá stopa (max MAX_INC)
        :param voice: vzorek hlasu
        Přidá do self.voiceStreams[player] zvukovou stopu v podobě (increment, voice)
        Pokud zjistí, že předchozí stopa má menší increment, zařadí se před ní
        Pokud má seznam vzorků u jednoho hráče větší délku než MAX_VOICE tak se první člen odstraní (tím se kontroluje maximální délka zpoždění hlasu)
        """
        data = np.fromstring(voice, np.int16)
        self.voiceStreams[player].add(increment, data)


    def addEffect(self, name):
        self.effectStreams.append(wave.open(name, "rb"))

    def newVVolume(self, v):
        self.vVolume = v

    def newMVolume(self, v):
        self.mVolume = v

    def newEVolume(self, v):
        self.eVolume = v

    def run(self):
        self.increment = 0
        while True:
            self.myCallback()
            self.increment += 1
            if self.increment > self.MAX_INC: self.increment = 0

    def myCallback(self):
        _time = time.clock()
        if self.nextSample:
            self.stream.write(self.nextSample)  #Pošlu zvuk do reproduktorů
            self.lastSample = self.nextSample
        elif self.lastSample:                   # This is dead
            self.stream.write(self.lastSample)
            self.lastSample = ""
        _time = time.clock()
        #print ("{0:d}  ---- {1:d} --- timeWrite: {2:.1f}".format(6 - self.voiceStreams.count([]) , self.stream.get_read_available(), (time.clock() - _time)* 1000)   , end = "   ")

        if self.stream.get_read_available() > 1023:
            mic = self.stream.read(1024)
        else:
            mic = ""
        #print ("timeRead: {0:.1f}".format(  (time.clock() - _time)* 1000)  , end = "   ")

        if mic: self.sendVoice.emit(mic, self.increment)             #Pošlu data z mikrofonu serveru

        _time = time.clock()
        data = np.zeros(2048, np.int64)

        length = 0        #Přeču data z VOIP serveru
        for v in self.voiceStreams:
            if v: length += 1
        l1 = length
        for v in self.voiceStreams:
            sample = v.get()
            if sample is not Buffer.DEFAULT:
                data += sample / length * self.vVolume * 0.4

        if self.musicStreams:                   #Přečtu vzorek zvukové stopy hudby
            wf = self.musicStreams[0]
            konec = int((wf.getnframes() -  wf.tell() ) / 1024)
            if (konec) < 250:   #Novou hudbu začnu přehrávat 250 CHUNKů před koncem poslední hudby

                if konec == 0:  #Jsem na konci
                    self.musicStreams.append(self.musicStreams.pop(0))  #Přesunu stopu na konec
                    wf.rewind()
                    frames = self.musicStreams[0].readframes(1024)
                    s = np.fromstring(frames, np.int16) * self.mVolume * 0.3

                else:
                    s0 = (np.fromstring(wf.readframes(1024), np.int16) / (250 - konec)) * self.mVolume * 0.3
                    if len(s0) > 2047:
                        data += s0
                    frames = self.musicStreams[1].readframes(1024)      #Je potřeba mít alespoň dvě stopy hudby
                    s = (np.fromstring(frames, np.int16) / (konec)) * self.mVolume * 0.3

            else:
                frames = wf.readframes(1024)
                s = np.fromstring(frames, np.int16) * self.mVolume * 0.3
            data += s

        length = len(self.effectStreams)        #Přečtu vzorky zvukových stop efektů
        toPop= []
        for i in range(length):
            s = self.effectStreams[i].readframes(1024)
            if s == "":
                toPop.append(i - len(toPop))
            else:
                d = np.fromstring(s, np.int16)
                if len(d) > 2047:
                    data += (d/ length * length)  * self.eVolume * 0.3

        for i in toPop:
            del self.effectStreams[i]

        if np.any(data):
            self.nextSample = data.astype(np.int16).tostring()  #Připravím si stopu pro čtení
        else:
            self.nextSample = data.astype(np.int16).tostring()


        #print ("timeRest: {0:.1f}".format(  (time.clock() - _time)* 1000), end = "    ||  ")
        #print("HOW MANY CHUNKS OF VOICE I GOT: ", l1)


    def close(self):
        self.timer.stop()
        self.stream.stop_stream()
        self.stream.close()

        self.p.terminate()


class Launcher(QQuickItem):
    PORTS = (9998, 9999)
    PORT = 9999
    SIZEOF_UINT32 = 4


    playersChanged = pyqtSignal()
    @pyqtProperty(QVariant, notify= playersChanged)
    def players(self):
        return self._players

    namesChanged = pyqtSignal()
    @pyqtProperty(QVariant, notify= namesChanged)
    def names(self):
        return self._names

    serverNameChanged = pyqtSignal()
    @pyqtProperty(str, notify= serverNameChanged)
    def serverName(self):
        return self._serverName

    @serverName.setter
    def serverName(self, name):
        self.client.sendMessage("jmeno_serveru", (name, ))

    meChanged = pyqtSignal()
    @pyqtProperty(int, notify=meChanged)
    def me(self):
        return self._me

    @pyqtProperty(QVariant)
    def write(self):
        return "a"

    @write.setter
    def write(self, text):
        text= text.toVariant()
        print (" // QML: ", text)


    @pyqtSlot()
    def _start(self):
        self.client.sendMessage("spust_hru", ())

    @pyqtSlot(float, float, float)
    def _changeVolume(self, voip, music, effect):
        self.sound.vVolume = voip
        self.sound.mVolume = music
        self.sound.eVolume = effect

    @pyqtSlot(str)
    def _connectTo(self, adresa):

        self.client.connectToServer(adresa)
        if self.client.socket.waitForConnected(3000):
           #print ("Připojeno")

            self.voip = C.VOIP(adresa)
            self.voip.newMessage.connect(self.addVoice)
            self.sound.sendVoice.connect(self.voip.writeDatagram)
            self.client.sendMessage("zmen_jmeno", (QN.QHostInfo.localHostName(),))


    @pyqtSlot()
    def _createServer(self):
        if not self.server:
            self.server = Process(target = S.run, args = (False, ))
            self.server.daemon = True
            self.server.start()
            #self.bstopServer.setEnabled(True)
            #self.bserver.setEnabled(False)

        self.client.connectToServer("127.0.0.1")

        if self.client.socket.waitForConnected(3000):
           #print ("Pripojeno")

            self.voip = C.VOIP("127.0.0.1")
            self.voip.newMessage.connect(self.addVoice)
            self.sound.sendVoice.connect(self.voip.writeDatagram)
            self.client.sendMessage("zmen_jmeno", (QN.QHostInfo.localHostName(),))

    disconnected = pyqtSignal()
    @pyqtSlot()
    def _disconnect(self):
       #print("REFERENCE:   ", sys.getrefcount(self.game))
        self.game = None
        if view.gWindow: view.gWindow.close()
        self.nScanThread.start()
        self.disconnected.emit()
        self.sound.voip = None
        self.voip.close()

        if not self.server: return
        self.server.terminate()     #Bye
        self.server.join()
        self.server = None

    @pyqtSlot()
    def _quit(self):
        if self.server:
            self.server.terminate()     #Pro jistotu
            self.server.join()
        app.exit()


    setVolume = pyqtSignal(float, float, float)
    addVoice = pyqtSignal(int, int, bytes)
    addMusic = pyqtSignal(str)
    addEffect = pyqtSignal(str)
    @pyqtSlot()
    def _completed(self):
        self.client.closed.connect(self._disconnect)
        self.addVoice.connect(self.resendVoice)
        self.addMusic.connect(self.sound.addMusic)
        self.addEffect.connect(self.sound.addEffect)
        self.setVolume.emit(self.sound.vVolume, self.sound.mVolume, self.sound.eVolume)

    @pyqtSlot()
    def _hoverButton(self):
        pass#self.sound.addEffect("Music/menu-hover.wav")

    @pyqtSlot()
    def _clickButton(self):
        self.sound.addEffect("Music/menu-click.wav")

    def resendVoice(self, p, i, b):
        self.sound.addVoice(p, i, b)

    def __init__(self, parent=None):
        super(Launcher, self).__init__(parent)
        self.f()


        self.soundThread = QThread()
        self.sound = Sound()
        self.sound.moveToThread(self.soundThread)
        self.soundThread.started.connect(self.sound.run)
        self.soundThread.start()


        self.server = None
        self.game = None

        self.voip = None

        self.client = C.Client()
        self.client.command.connect(self.command)

        self.nScanThread = QThread()
        self.nScan = C.NetworkScan()
        self.nScan.addServer.connect(self.pridejServer)
        self.nScan.removeServer.connect(self.odstranServer)
        self.nScan.moveToThread(self.nScanThread)
        self.nScanThread.started.connect(self.nScan.run)
        self.nScanThread.finished.connect(self.nScan.close)


        self._turnedOn = False
        self._players = []
        self._names = []
        self._name = "MyName"
        self._serverName = ""
        self._me = 0

        self.serverList = []

        self.nScanThread.start()

       #print ("BEZI ZVUK", self.soundThread.isRunning())

    addServer = pyqtSignal(int, str, str, str, str)
    def pridejServer(self, index, adresa, jmeno, hraci, aktivni):
        if index != -1:
            self.serverList[index] = (adresa, jmeno, hraci, aktivni)
        else:
            self.serverList.append((adresa, jmeno, hraci, aktivni))

        self.addServer.emit(index, adresa, jmeno, "{0:d}/6".format(hraci), aktivni and "In Game" or "Waiting")

    removeServer = pyqtSignal(int)
    def odstranServer(self, index):
        del self.serverList[index]
        self.removeServer.emit(index)

    def command(self, h, nazev, args):
        self.zadavatel= h
        try:
            self.funkce[nazev](args)
        except KeyError: pass

    def nove_spojeni(self, args):
        self._players[self.zadavatel] = True
        self.playersChanged.emit()

    def odpojeni_hrace(self, args):
        self._players[self.zadavatel] = False
        self._names[self.zadavatel] = ""

        self.playersChanged.emit()
        self.namesChanged.emit()

    renameServer = pyqtSignal(str)
    def jmeno_serveru(self, args):
        #self._serverName = args[0]
        #self.serverNameChanged.emit()   #To bohužel nefunguje
        self.renameServer.emit(args[0])

    connected = pyqtSignal()
    def pripojen(self, args):
        self.nScan.go = False
        self._players = args[0]
        self._names = args[1]
        self._serverName = args[2]
        self._me = self.zadavatel


        self.connected.emit()
        self.serverNameChanged.emit()
        self.playersChanged.emit()
        self.namesChanged.emit()
        self.renameServer.emit(args[2])
        self.setVolume.emit(self.sound.vVolume, self.sound.mVolume, self.sound.eVolume)

    def zmen_jmeno(self, args):
        self._names[self.zadavatel] = args[0]
        self.namesChanged.emit()

    def spust_hru(self, args):
        pass

    def priprava_mapy(self, args):
        self.mapa= game.Mapa(*args)

    def priprava_hrace(self, args):
        self._me= args

    def priprava_hracu(self, args):
        """
        :param args: tuple(data o hráčích)
        nejdříve inicializuje hráče a pak grafickou stránku hry
        """
        self.mapa.nacti_hrace(self._me, args[0])
        view.launchGame()
        self.game= view.gWindow.rootObject()
        self.game.priprava_hry(self.mapa, len(args[0]))

    def priprava_kola(self, args):
        self.client.command.disconnect()

        self.game.priprava_kola(*args)

        self.game.setClient(self.client)
        self.game.setSound(self.sound)


    def chyba(self, args):
       print ("KLIENT: Nastala chyba na straně serveru: ", args)

    def chybna_akce(self, args):
       print ("KLIENT: Tento požadavaek nelze splnit: ", args)

    def ignore(self, argumenty): pass

    def f(self):
        self.funkce= {
            "nove_spojeni": self.nove_spojeni,
            "odpojeni_hrace": self.odpojeni_hrace,
            "zmen_jmeno": self.zmen_jmeno,
            "spust_hru": self.spust_hru,
            "pripojen": self.pripojen,
            "priprava_mapy": self.priprava_mapy,
            "priprava_hrace": self.priprava_hrace,
            "priprava_hracu": self.priprava_hracu,
            "priprava_kola": self.priprava_kola,
            "jmeno_serveru": self.jmeno_serveru,
            #"nove_pripojeni": self.ignore,
            #"server_info": self.ignore,

            "chyba": self.chyba,
            "chybna_akce": self.chybna_akce,
        }

class Game(QQuickItem):



    #      PROPERTIES --------------------------- PROPERTIES

    parasitesChanged = pyqtSignal()
    @pyqtProperty(QVariant, notify= parasitesChanged)
    def parasites(self):
        return self._parasites

    bloodChanged = pyqtSignal()
    @pyqtProperty(QVariant, notify= bloodChanged)
    def blood(self):
        return self._blood

    itemCardsLeftChanged = pyqtSignal()
    @pyqtProperty(int, notify= itemCardsLeftChanged)
    def itemCardsLeft(self):
        return self._itemCardsLeft

    parasiteTurnChanged = pyqtSignal()
    @pyqtProperty(int, notify= parasitesChanged)
    def parasiteTurn(self):
        return self._parasiteTurn

    playingChanged = pyqtSignal()
    @pyqtProperty(int, notify= playingChanged)
    def playing(self):
        return self._playing

    openedDoorChanged = pyqtSignal()
    @pyqtProperty(int, notify= openedDoorChanged)
    def openedDoor(self):
        return self._openedDoor

    roomCardsLeftChanged = pyqtSignal()
    @pyqtProperty(int, notify= roomCardsLeftChanged)
    def roomCardsLeft(self):
        return self._roomCardsLeft

    meetingChanged = pyqtSignal()
    @pyqtProperty(QVariant, notify= meetingChanged)
    def meeting(self):
        return self._meeting

    meChanged = pyqtSignal()
    @pyqtProperty(int, notify= meChanged)
    def me(self):
        return self._me

    positionsChanged = pyqtSignal()
    @pyqtProperty(QVariant, notify= positionsChanged)
    def positions(self):
        return self._positions

    hitPointsChanged = pyqtSignal()
    @pyqtProperty(QVariant, notify= hitPointsChanged)
    def hitPoints(self):
        return self._hitPoints

    avatarsChanged = pyqtSignal()
    @pyqtProperty(QVariant, notify= avatarsChanged)
    def avatars(self):
        return self._avatars

    cardsOnBoardChanged = pyqtSignal()
    @pyqtProperty(QVariant, notify= cardsOnBoardChanged)
    def cardsOnBoard(self):
        return  self._cardsOnBoard

    namesChanged = pyqtSignal()
    @pyqtProperty(QVariant, notify=namesChanged)
    def names(self):
        return self._names

    ammosChanged = pyqtSignal()
    @pyqtProperty(QVariant, notify= ammosChanged)
    def ammos(self):
        return self._ammos

    cardsChanged = pyqtSignal()
    @pyqtProperty(QVariant, notify= cardsChanged)
    def cards(self):
        return self._cards

    connectionsChanged = pyqtSignal()
    @pyqtProperty(QVariant, notify= connectionsChanged)
    def connections(self):
        return self._connections

    nextRoomChanged = pyqtSignal()
    @pyqtProperty(str, notify= nextRoomChanged)
    def nextRoom(self):
        return self._nextRoom

    cardsInHandChanged = pyqtSignal()
    @pyqtProperty(QVariant, notify= cardsInHandChanged)
    def cardsInHand(self):
        return self._cardsInHand

    corruptedChanged = pyqtSignal()
    @pyqtProperty(bool, notify= corruptedChanged)
    def corrupted(self):
        return self._corrupted

    @pyqtProperty(QVariant)
    def write(self):
        return "a"

    @write.setter
    def write(self, text):
        text= text.toVariant()
        print (" // QML: ", text)

    timeToChanged= pyqtSignal()
    @pyqtProperty(int, notify= timeToChanged)
    def timeTo(self):
        return self._timeTo

    actionPointsChanged= pyqtSignal()
    @pyqtProperty(int, notify= actionPointsChanged)
    def actionPoints(self):
        return self._actionPoints

    humanChanged = pyqtSignal()
    @pyqtProperty(int, notify= humanChanged)
    def human(self):
        return self._human

    @human.setter
    def human(self, i):
        self._human = i
        self.humanChanged.emit()



    #      SLOTS ------------------------------- SLOTS

    @pyqtSlot()
    def _endTurn(self):
        self.send("konec_kola", ())

    @pyqtSlot(QVariant)
    def _newMeeting(self, pohyb):
        pohyb = [int(i) for i in pohyb.toVariant()]
        self._meeting = self.mapa.setkani(self._me, self._human, pohyb, True)
        self.meetingChanged.emit()

    pickPlayer= pyqtSignal(QVariant, str)
    @pyqtSlot(int)
    def _pickPlayer(self, clovek):
        """
        :param clovek: mluví za vše

        Zjistí s kým se hráč v místnosti setká, v jaké místnosti je, a jaké akce zde může použít
        """
        akce = [False, False, False, False]
        if self.mapa.hrac.ma_predmet("Scanner") and self._meeting: akce[0] = True
        if self.mapa.hrac.naboje and self._meeting: akce[1] = True
        if self.mapa.hrac.ma_predmet("Grenade"): akce[2] = True
        if self.mapa.hrac.vylozeno[0] and self._meeting: akce[3] = True
        y, x = self.mapa.hrac.pos[clovek]
        mistnost = self.mapa.mapakaret[y][x][0]
        self.pickPlayer.emit(akce, mistnost)

    tryHeal = pyqtSignal(int)
    @pyqtSlot(str)
    def _useCard(self, jmeno):
        if jmeno == "FirstAid": self.tryHeal.emit(-1)
        elif jmeno == "EnergyDrink": self.send("energit", ())
        elif jmeno in ("Ammo", "Riffle", "Scope", "Card", "Knife"): self.send("vyloz_kartu", (jmeno, ))

    @pyqtSlot(str, int, int, int)         #karta, clovek(ja), cil(jm)
    def _changeCards(self, karta, clovek, jmT, clovekT):
       #print("budou se menit karty")
        self.send("vymen_kartu", (karta, clovek, jmT, clovekT))

    @pyqtSlot(int)
    def _cover(self, clovek):
        self.send("kryti_vestou", (clovek, ))

    tryMove = pyqtSignal(int, int)
    @pyqtSlot(int, int, int)
    def _tryMove(self, y, x, clovek):
        """
        Zjistí jestli je možné se do místnosti pohnout
        """
        y1, x1 = self.mapa.hrac.pos[clovek]
        yp, xp = y - y1, x - x1
        if not((yp in (1, -1) and xp == 0) or (xp in (1, -1) and yp == 0)): return  #Kontroluji, jestli se pohybuje pouze o jedno políčko
        if self.mapa.kolize(self._me, clovek, (yp, xp)): return  #Musí tam být průchod
        self.tryMove.emit(y, x)

    @pyqtSlot(int, int, int)
    def _movePlayer(self, y, x, clovek):
        y1, x1 = self.mapa.hrac.pos[clovek]
        pohyb = (y - y1, x - x1)
        self.send("pohyb_hrace", (clovek, pohyb))

    @pyqtSlot(int, int, int, int)
    def _drawCard(self, clovek, jmT, clovekT, parazit):
        if parazit > -1: jmT = self._me
        self.send("prohledat_mistnost", (clovek, jmT, clovekT))

    @pyqtSlot()
    def _burn(self):
        self.send("vypal_hnizdo", ())

    @pyqtSlot(int, int)
    def _heal(self, clovek, h):
        self.send("vylecit_nem", (clovek, h))

    @pyqtSlot(int, int)
    def _healPlayer(self, h1, h2):
        self.send("vylecit_kar", (h1, h2))

    @pyqtSlot(int)
    def _scan(self, clovek):
        self.send("plosny_scan", (clovek, ))

    @pyqtSlot(int, int, int)
    def _scanPlayer(self, clovek, jmT, clovekT):
       #print("scan")
        self.send("scan", (clovek, jmT, clovekT))

    @pyqtSlot(int)
    def _openDoors(self, clovek):
        self.send("otevri_dvere", (clovek, ))

    @pyqtSlot(int, QVariant)
    def _throwGrenade(self, clovek, pohyb):
        pohyb= [int(i) for i in pohyb.toVariant()]
        self.send("granat", (clovek, pohyb))

    @pyqtSlot(int, int ,int)
    def _stab(self, jmT, clovekT, parazit):
        if parazit > -1: cil= (parazit, None)
        else: cil= (jmT, clovekT)
        self.send("bodnuti", cil)

    @pyqtSlot(int, int, int, QVariant)
    def _shoot(self, jmT, clovekT, parazit, pohyb):
        pohyb= [int(i) for i in pohyb.toVariant()]
        if parazit > -1: self.send("strelba", (parazit, None, pohyb))
        else: self.send("strelba", (jmT, clovekT, pohyb))


    @pyqtSlot()
    def _spawn(self):
        self.send("spawn", ())

    @pyqtSlot(int, int, int, int)
    def _placeRoom(self, clovek, y, x, reversed):
        """ Zkontroluje, jestli je na souřadnicích y,x objevit místnost, a odešle příkaz na server """
        argumenty= self.mapa._objevit_mistnost(clovek, y, x, reversed)
        if argumenty:
            self.send("objevit_mistnost", (argumenty))


    @pyqtSlot()
    def _close(self):
       #print ("QUIT")
        view.gWindow.close()


    #     -----------------POMOCNÉ FUNKCE-------------------

    def close(self):
        view.gWindow = None
        self.client.command.disconnect()
        self.client.command.connect(view.rootObject().command)
        if not self.END: view.rootObject()._disconnect()

    def updateMeeting(self, pohyb= (0, 0)):
        """
         vytvoří nový seznam setkání (používá se při pušce a granátu)
        :param mistnost: určuje směr setkání
        """
        self._meeting= self.mapa.setkani(self._me, self._human, pohyb, True)
        self.meetingChanged.emit()

    def timer(self):
        """
        Upraví čas na odpočtu každou sekundu...
        """
        if self.pauza or self._timeTo < 1: return
        self._timeTo -= 1
        self.timeToChanged.emit()

    def addToHand(self, hrac, predmet):
        self._cards[hrac]+=1
        self.cardsChanged.emit()
        if hrac != self._me: return
        if predmet[:-1] == "Blood": return
        if not self.mapa.hrac.predmety[predmet]:    # Hráč nemá předmět, a proto budu muset appendovat do _cardsInHand
            self._cardsInHand.append([predmet, 1])
        else:                                       # Najdu pozici předmetu v _cardsInHand a zvýším jeho počet o jedna
            for i in range(len(self._cardsInHand)):
                if self._cardsInHand[i][0] == predmet:
                    self._cardsInHand[i][1] += 1
                    break

        self.newItem.emit(predmet)
        self.cardsInHandChanged.emit()

    def removeFromHand(self, hrac, predmet):
        self._cards[hrac] -= 1
        self.cardsChanged.emit()
        if hrac != self._me: return


        if predmet[:-1] == "Blood": return

        if self.mapa.hrac.predmety[predmet] == 1:
            self._cardsInHand.remove([predmet, 1])
        else:                               #Najdu pozici předmetu v _cardsInHand a snížím jeho počet o jedna
            for i in range(len(self._cardsInHand)):
                if self._cardsInHand[i][0] == predmet:
                    self._cardsInHand[i][1] -= 1
                    break
        self.cardsInHandChanged.emit()

    def action(self):
        self._actionPoints -=1
        self.actionPointsChanged.emit()


    def __init__(self, parent= None):
        super(Game, self).__init__(parent)
        self.f()

        self._connections= []
        self._positions = []
        self._hitPoints = []
        self._avatars = []
        self._cardsOnBoard = []
        self._ammos = []
        self._cards = []
        self._cardsInHand= []
        self._meeting = []
        self._parasites= []
        self._blood= []
        self._names= []

        self._nextRoom= ""

        self._timeTo = 100
        self._actionPoints = 0
        self._me = 0
        self._itemCardsLeft = 0
        self._roomCardsLeft = 0
        self._parasiteTurn= 0
        self._playing= 0
        self._openedDoor= -1
        self._human = 1

        self._corrupted = False
        # ----


        self.mapa = None
        self.hraje = None
        self.pauza = True
        self.casNaKolo = 100

        self.odpocet = QTimer(self)
        self.odpocet.timeout.connect(self.timer)
        self.odpocet.start(1000)

        self.END = False


    def setClient(self, client):
        self.client= client
        self.send= client.sendMessage

        self.client.command.connect(self.proved)
        view.gWindow.closed.connect(self.close)


    addMusic = pyqtSignal(str)
    addEffect = pyqtSignal(str)
    def setSound(self, sound):
        self.addMusic.connect(sound.addMusic)
        self.addEffect.connect(sound.addEffect)
        self.sound = sound


    def pristi_mistnost(self):
        self._nextRoom= str(self.mapa.pristimistnost[3])
        self._roomCardsLeft -= 1
        self.roomCardsLeftChanged.emit()
        self.nextRoomChanged.emit()

    def proved(self, h, nazev, args):
        self.zadavatel= h
        self.funkce[nazev](args)

    def nove_spojeni(self, args):
        """
        :param args: int(index hráče)
        """
        self._connections[self.zadavatel] = True
        # Hráč se připojil

    def odpojeni_hrace(self, args):
        """
        :param args: int(index hráče)
        """
        self._connections[args[0]] = False
        self.connectionsChanged.emit()
        # Hráč se odpojil

    def pripojeni_hrace(self, args):
        self._connections[self.zadavatel] = True
        self.connectionsChanged.emit()

    newRoom = pyqtSignal(int, int, str, int, bool)     #Přidá místnost na mapu
    def priprava_hry(self, mapa, pocet):
        self.mapa= mapa
        self._me = mapa.ja
        self._connections= ["connected" for _ in range(pocet)]
        self.pristi_mistnost()
        #Vykreslím mapu
        for y, r in enumerate(self.mapa.mapakaret):
            for x, m in enumerate(r):
                if m:
                    prevratit = m.pop() and 1 or 0
                    pouzita = m[-2] and True or False
                    self.newRoom.emit(y, x, m[-1], prevratit, pouzita)
        #Inicializuji hráče (mě)
        self._cardsInHand = self.mapa.hrac.seznamPredmetu()
        self._corrupted = self.mapa.hrac.nakazeny
        self.corruptedChanged.emit()
        self._blood = self.mapa.hrac.krve
        #Inicializuji hráče (ostatní)
        for hrac in self.mapa.hraci:
            me = hrac.me()
            self._positions.append(me[0])
            self._hitPoints.append(me[1])
            self._avatars.append(me[2])
            self._cardsOnBoard.append(me[3])
            self._names.append(me[4])
            self._ammos.append(me[5])
            self._cards.append(me[6])

        #Inicalizuji proměnné
        self._parasites = self.mapa.paraziti

        self.positionsChanged.emit()
        self.hitPointsChanged.emit()
        self.avatarsChanged.emit()
        self.cardsOnBoardChanged.emit()
        self.namesChanged.emit()
        self.ammosChanged.emit()
        self.cardsChanged.emit()

        self.connectionsChanged.emit()
        self.cardsInHandChanged.emit()
        self.bloodChanged.emit()
        self.parasitesChanged.emit()

        for i in range(len(self._positions)):
            if self._positions[i][0][0] > -1 or self._positions[i][1][0] > -1:
                self.spawnPlayer.emit(i)  # Pokud jsem se odpojil a připojil!

    def priprava_kola(self, hraje, koloP, zMistnosti, zKarty, dvere, ap):
        """
        :param hraje: int(kdo hraje)
        :param koloP: int(kdy hraji paraziti)
        :param zMistnosti: int(kolik zbyva mistnosti)
        :param zKarty: int(kolik zbyva karet)
        :param dvere: bool(jsou dvere otevrene)
        :param ap: int(kolik zbyva akcnich bodu)
        """
        self._playing = hraje
        self._parasiteTurn = koloP
        self._roomCardsLeft = zMistnosti
        self._itemCardsLeft = zKarty
        self._openedDoor = dvere
        self._actionPoints = ap

        self.mapa.otevrenedvere= dvere

        self.playingChanged.emit()
        self.parasiteTurnChanged.emit()
        self.itemCardsLeftChanged.emit()
        self.roomCardsLeftChanged.emit()
        self.openedDoorChanged.emit()
        self.actionPointsChanged.emit()

    changeCards = pyqtSignal(int)      # Budou se měnit karty
    def pohyb_hrace(self, args):
        """
        :param args: int(klon|clovek), tuple(pohyb), tah
        :return:
        """
        clovek, pohyb, tah= args
        setkani = self.mapa.pohyb_hrace(self.zadavatel, clovek, pohyb)  #Tohle už s ním pohne
        #self._positions[self.zadavatel][clovek] = self.mapa.hraci[self.zadavatel].pos[clovek]
        self.positionsChanged.emit()
        if setkani != [[0, 0, 0]] and self.zadavatel == self._me:
            self._meeting= setkani
            self.meetingChanged.emit()
            self.changeCards.emit(clovek)
           #print("vymena karet", clovek, self._meeting)

        if tah: self.action()


    placeRoom = pyqtSignal(int, int, int, int, int) #Objev místnost
    def objevit_mistnost(self, args):
        """
        :param args: list, int, int, int, int, int  (Viz dole)
        obnoví příští_místnost + přidá místnost na mapu
        """
        pos, mistnost, prevratit, pmistnost, jm, clovek= args   #pmistnost = pristi mistnost
        self.mapa.objevit_mistnost(pos, mistnost, prevratit, pmistnost)

        self.placeRoom.emit(pos[0], pos[1], prevratit, jm, clovek)
        self.pristi_mistnost()

        self.action()

    changingCards = pyqtSignal(int, int, int, int)
    def vymen_kartu(self, args):
        """
        Tady by asi stálo za to, trošku podrobnějí rozebrat tu šílenou změť signálů při výměně karet:
        Po pohybu hráče se zkontroloje s kým se v místnosti setkal, pokud se tak stane, odešle se do hry signál "changeCards" ->
        -> to znamená že si hráč vybere s kým bude měnit a jakou kartu vymění - až to udělá, zavolá se slot "_changecards" ->
        -> to způsobí odeslání požadavku na server, který pak odpoví příkazem "vymen_kartu" což emitne signál "changingCards" ->
        -> v této chvíli dostane druhý hráč požadavek o výměnu své karty a požadavek se poté opět odešle na server a ten pak vrátí odpoveď "vymena_karet" ->
        -> signál "allCardsChanged": teď teprve se oběma hráčům zobrazí karty, které dostaly od spoluhráče a hra může pokračovat dál
        UFF...

        :param args: int(clovek|klon -- pro prvního hráče), int(index druhého hráče), int(clovek|klon -- pro druhého hráče)
        Vykreslí na mapě akci výměny mezi hráči
        """
        if args[1] == self._me:
            self._meeting= [[False, False, self.zadavatel], [0, 0, 0]]
            self._meeting[0][args[0]] = True
            self.meetingChanged.emit()
        self.changingCards.emit(self.zadavatel, *args)

    allCardsChanged = pyqtSignal(str)
    def vymena_karet(self, args):
        """
        Odeberu hráči odevzdaný předmět a dám mu nový
        :param args: list(karta2, karta1)
        """
       #print("VYMENA", args)
        if self._playing == self._me:
            k1, k2, nakazeny = args
        else:
            k2, k1, nakazeny = args

        if not self._corrupted and nakazeny == self._me:
            self._corrupted = True
            self.corruptedChanged.emit()

        self.allCardsChanged.emit(k1)

        if k1 != k2:
            self.addToHand(self._me, k1)
            self.removeFromHand(self._me, k2)

        self.mapa.hrac.spravuj_predmet(k1, 1)
        self.mapa.hrac.spravuj_predmet(k2, -1)

        self.bloodChanged.emit()        # Pro případ, že by se měnili krve


    shootPlayer = pyqtSignal(int, int, int, QVariant, int)
    shootParasite = pyqtSignal(int, int, QVariant, int)
    def strelba(self, args):
        """
        :param args: int(poskozeni), tuple(cil), tuple(pohyb)
        """
        self.sound.addEffect("Music\gun-shot.wav")
        poskozeni, jmT, clovekT, pohyb = args
        self.mapa.hraci[self.zadavatel].odeber_naboje(poskozeni)
        self._ammos[self.zadavatel] -= poskozeni
        self.ammosChanged.emit()
        if clovekT is None:
            pozice = self.mapa.hraci[self.zadavatel].pos[0][:]
            pozice[0] += pohyb[0]
            pozice[1] += pohyb[1]
            mrtvy= self.mapa.zranit_parazita(pozice, jmT)
            #self._parasites = self.mapa.paraziti
            self.parasitesChanged.emit()
            self.updateMeeting()
            self.shootParasite.emit(self.zadavatel, jmT, pohyb, poskozeni)
        else:
            self.shootPlayer.emit(self.zadavatel, jmT, clovekT, pohyb, poskozeni)


    stabPlayer= pyqtSignal(int, int, int, int)
    stabParasite= pyqtSignal(int, int, int)
    def bodnuti(self, args):
        """
        Ubere hráčům životy a vykreslí bodnutí
        :param args: bool(povedlo se?), int(ind), tuple(cil)
        """
        self.sound.addEffect("Music\slash.wav")
        poskozeni, jmT, clovekT = args
        if clovekT is None:
            if poskozeni:
                pozice = self.mapa.hraci[self.zadavatel].pos[1]
                mrtvy= self.mapa.zranit_parazita(pozice, jmT)
                #self._parasites = self.mapa.paraziti
                self.parasitesChanged.emit()
                self.updateMeeting()
            else:
                mrtvy = False
            self.stabParasite.emit(self.zadavatel, jmT, poskozeni)
        else:
            mrtvy= self.mapa.hraci[jmT].zranit(poskozeni, clovekT)
            #self._hitPoints[jmT]= self.mapa.hraci[clovekT].zivoty
            self.stabPlayer.emit(self.zadavatel, jmT, clovekT, poskozeni)
            self.hitPointsChanged.emit()
            self.positionsChanged.emit()    #Kdyby někdo umřel
        self.action()


    throwGrenade = pyqtSignal(int, int, QVariant)
    def granat(self, args):
        """        
        Ubere hráčům životy a vykreslí hod granátem
        :param args: ind, pohyb
        """
        clovek, pohyb= args

        zraneni = [[False, False] for _ in range(len(self._connections))] + [[0, 0]]
        y = self.mapa.hraci[self.zadavatel].pos[clovek][0] + pohyb[0]
        x = self.mapa.hraci[self.zadavatel].pos[clovek][1] + pohyb[1]
        for i, h in enumerate(self.mapa.hraci):
            if h.pos[0] == [y, x]:
                zraneni[i][0] = True
                h.zranit(1, 0)
            if h.pos[1] == [y, x]:
                zraneni[i][1] = True
                h.zranit(1, 1)
        paraziti = []
        for p in self.mapa.paraziti:
            if p[0] == [y, x]:
                if p[2] == 2:
                    paraziti.append([p[0], p[1], 1])
                    zraneni[-1][1] += p[1]
                else:
                    zraneni[-1][0] += p[1]
            else:
                paraziti.append(p)

        self.sound.addEffect("Music\grenade-throw.wav")

        self._parasites = self.mapa.paraziti = paraziti


        self.throwGrenade.emit(self.zadavatel, clovek, zraneni)


        self.removeFromHand(self.zadavatel, "Grenade")
        self.mapa.hraci[self.zadavatel].spravuj_predmet("Grenade", -1)

        self.disableMovement.emit()     #Aby mi paraziti nelítaly přes celou mapu
        self.parasitesChanged.emit()
        self.hitPointsChanged.emit()
        self.positionsChanged.emit()    #Kdyby někdo umřel
        self.action()

    healPlayer = pyqtSignal(int)
    def vylecit_kar(self, args):
        """
        :param args: int(+HP klon), int(+HP člověk)
        """
        self.removeFromHand(self.zadavatel, "FirstAid")
        self.mapa.hraci[self.zadavatel].vylecit(*args)

        #self._hitPoints[self.zadavatel] = self.mapa.hraci[self.zadavatel].zivoty
        self.hitPointsChanged.emit()
        self.healPlayer.emit(self.zadavatel)

    heal = pyqtSignal(int, int)
    def vylecit_nem(self, args):
        """
        :param args: int(clovek), int(+HP)
        """
        self.mapa.hraci[self.zadavatel].zivoty[args[0]] += args[1]
        #self._hitPoints[self.zadavatel] = h.zivoty
        self.hitPointsChanged.emit()
        self.heal.emit(self.zadavatel, args[0])

    redBull = pyqtSignal(int)
    def energit(self, args):
        """ Přidá dva tahy navíc  """
        self.removeFromHand(self.zadavatel, "EnergyDrink")
        self.mapa.hraci[self.zadavatel].spravuj_predmet("EnergyDrink", -1)
        self._actionPoints += 2
        self.actionPointsChanged.emit()
        self.redBull.emit(self.zadavatel)

    def konec_kola(self, args):
        self.pauza = True

        self._playing= -1
        self.playingChanged.emit()


    newTurn= pyqtSignal(int)
    def nove_kolo(self, args):
        self._playing= args[0]
        if self.mapa.otevrenedvere == self._playing:
            self.mapa.otevrenedvere = self._openedDoor = -1
            self.openedDoorChanged.emit()
        self.newTurn.emit(self.hraje)
        self.pauza= False

        self._timeTo= self.casNaKolo
        self._actionPoints= self.mapa.hraci[self._playing].tahy()

        self.timeToChanged.emit()
        self.playingChanged.emit()
        self.actionPointsChanged.emit()


    spawnPlayer = pyqtSignal(int)
    def spawn(self, args):
        self.mapa.hraci[self.zadavatel].spawn()
        #self.positions[self.zadavatel] = self.mapa.hraci[self.zadavatel].pos
        self.positionsChanged.emit()
        self.spawnPlayer.emit(self.zadavatel)

    scanPlayer = pyqtSignal(int, int, int, int, QVariant, QVariant)  #Skenoval jsem já
    def scan(self, args):
        """
        Zobrazí karty cílového hráče
        :param args: list(seznam karet) -- nepovinne, int (cil)
        :return:
        """
        self.removeFromHand(self.zadavatel, "Scanner")
        self.mapa.hraci[self.zadavatel].spravuj_predmet("Scanner", -1)
        if self.zadavatel == self._me:
            self.scanPlayer.emit(self.zadavatel, *args)
        else:
            self.scanPlayer.emit(self.zadavatel, args[0], args[1], args[2], [], [])

        self.action()

    scanAllPlayers = pyqtSignal(int, int, int)
    def plosny_scan(self, args):
        """
        Zobrazí počet nakažených hráčů
        :param args: int(clovek| klon), int(počet nakažených)
        """
        self.scanAllPlayers.emit(self.zadavatel, *args)
        QTimer.singleShot(1000, lambda: self.sound.addEffect("Music\scream.wav"))
        self.action()

    openDoors = pyqtSignal(int ,int)
    def otevri_dvere(self, args):
        self.action()
        self._openedDoor = self.mapa.otevrenedvere = self.zadavatel
        self.openDoors.emit(self.zadavatel, args[0])
        self.openedDoorChanged.emit()

    burn = pyqtSignal(int)
    def vypal_hnizdo(self, args):
        """   ! GangBang !  """
        self.burn(self.zadavatel)

    useCard = pyqtSignal(int, str)
    def vyloz_kartu(self, args):
        self.removeFromHand(self.zadavatel, args[0])
        self.mapa.hraci[self.zadavatel].vyloz_predmet(args[0])
        self.useCard.emit(self.zadavatel, args[0])
        if args[0] == "Ammo":
            self._ammos[self.zadavatel] = self.mapa.hraci[self.zadavatel].naboje
            self.ammosChanged.emit()
        else:
            #self._cardsOnBoard[self.zadavatel] = self.mapa.hraci[self.zadavatel].vylozeno
            self.cardsOnBoardChanged.emit()


    parasiteMovement = pyqtSignal(QVariant)     #Udělí zranění a počká na použití vest
    def pohyb_parazitu(self, args):
        """
        Zobrazí přesun parazitů
        :param args: příští kolo parazitů, pohyb, zranění hráči
        """

        paraziti = self.mapa.pohyb_parazitu(args[0])

        self.parasitesChanged.emit()

        QC.QTimer.singleShot(620, lambda : self.poPohybu(paraziti, args[1]))

        self.parasiteTurnChanged.emit()

    #pohyb_parazitu a poPohybu patří k sobě

    disableMovement= pyqtSignal()    #Zruší dočasně animace pohybu parazitů
    def poPohybu(self, paraziti, zraneni):
        self.disableMovement.emit()
        self._parasites = self.mapa.paraziti = paraziti
        self.parasitesChanged.emit()
        if zraneni:
            self.parasiteMovement.emit(zraneni)

    turnAround = pyqtSignal(int, int)
    def otoc_mistnost(self, args):
        y, x = args
        self.mapa.mapakaret[y][x][-1] = False
        self.turnAround.emit(y, x)

    summonParasite = pyqtSignal(QVariant, int)
    def vyvolej_parazita(self, args):
        if args[0] is not None:     #Přitáhnu parazita
            i, souradnice = args
            self.mapa.pritahni_parazita(i, souradnice)
        else:                       #Vytvořím parazita
            self.mapa.vyvolej_parazita(args[1])
            self.summonParasite.emit(*args[1])

        #self._parasites= self.mapa.paraziti
        self.parasitesChanged.emit()

    shootResult = pyqtSignal(int, int, int, int)
    def hrac_utoci(self, args):
        jm, jmT, clovekT, poskozeni= args
        mrtvy= self.mapa.hraci[jmT].zranit(poskozeni, clovekT)
        #self._hitPoints[cil[1]]= self.mapa.hraci[cil[1]].zivoty
        self.shootResult.emit(jm, jmT, clovekT, poskozeni)
        self.hitPointsChanged.emit()
        self.positionsChanged.emit()    #Kdyby někdo umřel
        self.action()

    parasiteAttackResult = pyqtSignal(QVariant)
    def paraziti_utoci(self, args):
        """
        :param args: seznam zraneni, pristiKoloParazitu
        """
        self._parasiteTurn= args[1]
        self.parasiteTurnChanged.emit()

        zraneni= args[0]
        if not zraneni: return
        for h, z in zip(self.mapa.hraci, zraneni):
            h.zranit(z[0], 0)
            h.zranit(z[1], 1)

        zraneni.append([0, 0])    # Paraziti ... - Aby se to mohlo vykreslit...

        self.parasiteAttackResult.emit(zraneni)
        self.hitPointsChanged.emit()
        self.positionsChanged.emit()    #Kdyby někdo umřel - odstraní ho z mapy

    def kryti_vestou(self, args):
        self.removeFromHand(self.zadavatel, "Vest")
        self.mapa.hraci[self.zadavatel].spravuj_predmet("Vest", -1)


    drawCard = pyqtSignal(int, int)
    newItem = pyqtSignal(str)           #Přidá hráči (mě) předmět
    def lizani_karet(self, args):
        """
        :param args:  jm int(hráč který si líznul kartu), clovek, tah, nepovinný : string(predmet)
        :return:
        """
        jm, clovek, tah = args[0], args[1], args[2]
        if len(args) == 4:
            predmet= args[3]
        else:
            predmet = ""
        if predmet != "Parasite":
            self.addToHand(jm, predmet)
            self.mapa.hraci[jm].spravuj_predmet(predmet, 1)
        else:
            if predmet == "Infection":
                self._corrupted = True
                self.corruptedChanged.emit()
            self.newItem.emit(predmet)

        self.drawCard.emit(jm, clovek)
        if tah: self.action()
        self._itemCardsLeft -= 1
        self.itemCardsLeftChanged.emit()
        self.updateMeeting()

    outOfCards = pyqtSignal()
    def dosly_karty(self, args):
        self.outOfCards.emit()

    endGame = pyqtSignal(bool)
    def konec(self, args):
        self.endGame.emit(args[0] is args[1][self._me])
        self.END = True
        self.pauza = True


    def chyba(self, args):
        print ("KLIENT: Nastala chyba na straně serveru: ", args)

    def chybna_akce(self, args):
        print ("KLIENT: Tento požadavek nelze splnit: ", args)

    def f(self):
        self.funkce= {
            "nove_spojeni": self.nove_spojeni,
            "odpojeni_hrace": self.odpojeni_hrace,
            "pripojeni_hrace": self.pripojeni_hrace,
            "pohyb_hrace": self.pohyb_hrace,
            "objevit_mistnost": self.objevit_mistnost,
            "vymen_kartu": self.vymen_kartu,
            "vymena_karet": self.vymena_karet,
            "strelba": self.strelba,
            "bodnuti": self.bodnuti,
            "granat": self.granat,
            "vylecit_kar": self.vylecit_kar,
            "vylecit_nem": self.vylecit_nem,
            "energit": self.energit,
            "konec_kola": self.konec_kola,
            "nove_kolo": self.nove_kolo,
            "spawn": self.spawn,
            "scan": self.scan,
            "plosny_scan": self.plosny_scan,
            "otevri_dvere": self.otevri_dvere,
            "vypal_hnizdo": self.vypal_hnizdo,
            "vyloz_kartu": self.vyloz_kartu,
            "pohyb_parazitu": self.pohyb_parazitu,
            "otoc_mistnost": self.otoc_mistnost,
            "vyvolej_parazita": self.vyvolej_parazita,
            "dosly_karty": self.dosly_karty,
            "lizani_karet": self.lizani_karet,
            "hrac_utoci": self.hrac_utoci,
            "paraziti_utoci": self.paraziti_utoci,
            "kryti_vestou": self.kryti_vestou,
            "konec": self.konec,
            "chyba": self.chyba,
            "chybna_akce": self.chybna_akce,
        }




class LauncherWindow(QQuickView):

    def __init__(self, parent=None):
        super(LauncherWindow, self).__init__(parent)
        #self.setFlags(QC.Qt.Window|QC.Qt.FramelessWindowHint)

        self.setSource(
            QUrl.fromLocalFile(
                find_data_file("LauncherUI\Launcher.qml")))
        self.setResizeMode(QQuickView.SizeViewToRootObject)


        self.setMaximumHeight(600)
        self.setMaximumWidth(800)
        self.setMinimumHeight(600)
        self.setMinimumWidth(800)

        self.center()

    def center(self):
        #Center the window
        desktop = QGuiApplication.primaryScreen().geometry()
        size = self.geometry()
        width, height = desktop.width(), desktop.height()
        mw, mh = size.width(), size.height()
        centerW = (width / 2) - (mw / 2)
        centerH = (height / 2) - (mh / 2)
        self.setPosition(centerW, centerH)


    def launchGame(self):
        self.gWindow = GameWindow()
        self.gWindow.showFullScreen()


class GameWindow(QQuickView):

    closed = pyqtSignal()
    def __init__(self, parent=None):
        super(GameWindow, self).__init__(parent)

        self.setSource(
            QUrl.fromLocalFile(
                find_data_file("GameUI\Game.qml")))
        self.setResizeMode(QQuickView.SizeRootObjectToView)

    def close(self):
        self.destroy()
        self.closed.emit()
        return True

    def event(self, e):
        if e.type() == QEvent.Close:
            return self.close()
        return QQuickView.event(self, e)


def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)

    return os.path.join(datadir, filename)

class QPythonBinding(QQuickItem):
    def __init__(self, parent=None):
        super(QPythonBinding, self).__init__(parent)

    addElement = pyqtSignal(str, str)   //addElement.emit("name", "value")

if __name__ == '__main__':
    freeze_support()
    import os
    import sys


    app = QGuiApplication(sys.argv)

    qmlRegisterType(Launcher, "ParanoiaLauncher", 1, 0, "App")
    qmlRegisterType(Game, "ParanoiaEngine", 1, 0, "App")

    view = LauncherWindow()


    view.show()


    app.exec_()