# -*- coding: utf-8 -*-
__author__ = 'Josef'
#!/usr/bin/env python3

import sys, os
import ServerControl
from PyQt5 import QtCore as QC
from PyQt5 import QtGui as QG
from PyQt5 import QtWidgets as QW
from PyQt5 import QtNetwork as QN
from random import randint, choice
from ast import literal_eval

from store import Sequence

PORT = 9999
SIZEOF_UINT32 = 4

class ServerDlg(QW.QPushButton):

    def __init__(self, parent=None):
        super(ServerDlg, self).__init__(
                "&Close Server", parent)
        self.setWindowFlags(QC.Qt.WindowStaysOnTopHint)

        self.tcpServer = QN.QTcpServer(self)

        #Zjistím si svojí IP adresu
        for address in QN.QNetworkInterface.allAddresses():
            if address != QN.QHostAddress.LocalHost and address.toIPv4Address(): break
        else: address = QN.QHostAddress.LocalHost

        #print(address.toString())

        self.tcpServer.listen(QN.QHostAddress("0.0.0.0"), PORT)     #Any address
        self.tcpServer.newConnection.connect(self.addConnection)
        self.connections = [None for _ in range(6)]
        self.connectionAddress = [None for _ in range(6)]
        self.players= {}

        self.clicked.connect(self.close)
        font = self.font()
        font.setPointSize(24)
        self.setFont(font)
        self.setWindowTitle("Server")


    def setup(self, gmsu):
        self.manazer = gmsu

        def change(game):
            if game:
                self.manazer = Game(self) # Protože vytvářím novou hru
            else:
                self.manazer = gmsu       # Gmsu je už inicializováno

        self.changeHandler = change

    def runGame(self, avatary, jmena, jmeno):
        self.connections= [c for c in self.connections if c]    # Vyčistím seznam spojení od prázdných míst
        self.connectionAddress= [c for c in self.connectionAddress if c]
        self.changeHandler(True)
        self.manazer.priprav_hru(avatary, jmena, jmeno)

    def closeGame(self):
        self.connections+= [None for _ in range(6 - len(self.connections))]
        self.connectionAddress+= [None for _ in range(6 - len(self.connectionAddress))]
        self.changeHandler(False)
        self.manazer.kontrola()

    def addConnection(self):
        clientConnection = self.tcpServer.nextPendingConnection()

        if not clientConnection.waitForReadyRead(500):
            self.manazer.server_info(clientConnection)
            return

        for i, c in enumerate(self.connections):
            if c is None:
                self.connections[i] = clientConnection
                self.connectionAddress[i] = clientConnection.peerAddress()
                break
        else:               # Maximálně šest hráčů
            self.manazer.server_info(clientConnection)
            return

        clientConnection.nextBlockSize = 0

        clientConnection.readyRead.connect(self.receiveMessage)
        clientConnection.disconnected.connect(lambda: self.removeConnection(i))
        clientConnection.error.connect(self.socketError)

        self.manazer.nove_spojeni(i)

        self.receiveMessage()

    def updatePlayers(self, inRoom):
        for i, b in enumerate(inRoom):
            adr = self.connectionAddress[i]
            if adr: self.players[adr] = b

    def receiveMessage(self):
        for i, s in enumerate(self.connections):
            if s is None: continue
            if s.bytesAvailable() > 0:
                stream = QC.QDataStream(s)
                stream.setVersion(QC.QDataStream.Qt_5_2)

                if s.nextBlockSize == 0:
                    if s.bytesAvailable() < SIZEOF_UINT32:
                        return
                    s.nextBlockSize = stream.readUInt32()
                if s.bytesAvailable() < s.nextBlockSize:
                    return

                nazev, argumenty= stream.readQString(), stream.readQString()
                sID =  s.socketDescriptor()
                self.manazer.proved(i, nazev, literal_eval(argumenty))
                s.nextBlockSize = 0

    def sendMessage(self, h, nazev, argumenty, hraci = (), odkryj= 0):
        for i, s in enumerate(self.connections):
            if not s: continue                      #Pokud na této pozici není žádný objekt spojení
            if hraci and i in hraci or not hraci:   #Pokud odesílám zprávu všem, nebo hráči z nepoviného argumentu
                args = str(argumenty)
            elif not odkryj: continue              #Když je "odkryj" na nule, neodešle se nic
            else:
                args = str(argumenty[:odkryj])
            reply = QC.QByteArray()
            stream = QC.QDataStream(reply, QC.QIODevice.WriteOnly)
            stream.setVersion(QC.QDataStream.Qt_5_2)
            stream.writeUInt32(0)           #Vyhrazuji místo pro délku zprávy
            stream.writeUInt32(h)           #Zapisuji zprávu
            stream.writeQString(nazev)      #Zapisuji zprávu
            stream.writeQString(args)       #Zapisuji zprávu
            stream.device().seek(0)         #Přesouvám se na začátek vlákna
            stream.writeUInt32(reply.size() - SIZEOF_UINT32)    #Zapisuji délku zprávy
            s.write(reply)                  #Odesílám zprávu

    def writeReply(self, connection, nazev, argumenty):
        args = str(argumenty)
        reply = QC.QByteArray()
        stream = QC.QDataStream(reply, QC.QIODevice.WriteOnly)
        stream.setVersion(QC.QDataStream.Qt_5_2)
        stream.writeUInt32(0)           #Vyhrazuji místo pro délku zprávy
        stream.writeUInt32(0)           #Zapisuji zprávu
        stream.writeQString(nazev)      #Zapisuji zprávu
        stream.writeQString(args)       #Zapisuji zprávu
        stream.device().seek(0)         #Přesouvám se na začátek vlákna
        stream.writeUInt32(reply.size() - SIZEOF_UINT32)    #Zapisuji délku zprávy
        connection.write(reply)

    def removeConnection(self, h):
        self.connections[h] = None
        #del self.players[self.connectionAddress[h]]
        self.connectionAddress[h] = None
        self.manazer.odpojeni_hrace(h)

    def socketError(self):
        pass

    def napis(self):
        pass
        #print ("FUNGUJE TOO")

class VOIP(QC.QObject):

    MYPORT = 9997
    PLAYERPORT = 9998

    RINTERVAL = 50


    def __init__(self, parent= None):
        super(VOIP, self).__init__(parent)

        self.udpSocket = QN.QUdpSocket(self)
        self.udpSocket.bind(QN.QHostAddress("0.0.0.0"), VOIP.MYPORT)

        self.udpSocket.readyRead.connect(self.processPendingDatagrams)

        self.players= {}
        self.connectionAddress = []

        self.history= (Sequence(), Sequence(), Sequence(), Sequence(), Sequence(), Sequence())

        self.resendTimer = QC.QTimer()
        self.resendTimer.setInterval(VOIP.RINTERVAL)
        self.resendTimer.timeout.connect(self.resend)
        self.resendTimer.start()

    def resend(self):
        return  # Počkejte si na verzi 1.1
        for s in self.history:
            for data in s:
                datagram = data[-1]   # Poslední je vždy vlákno
                for i in range(6):
                    if not data[i]:
                        self.udpSocket.writeDatagram(datagram, self.connectionAddress[i], VOIP.PLAYERPORT)

    def answer(self, address, number):
        request = QC.QByteArray()

        stream = QC.QDataStream(request, QC.QIODevice.WriteOnly)
        stream.setVersion(QC.QDataStream.Qt_5_2)
        stream.writeBool(False)
        stream.writeUInt8(number)

        self.udpSocket.writeDatagram(request, address, VOIP.PLAYERPORT)

    def processPendingDatagrams(self):

        while self.udpSocket.hasPendingDatagrams():
            datagram, host, port = self.udpSocket.readDatagram(self.udpSocket.pendingDatagramSize())

            if host not in self.players or not self.players[host]: continue

            data = QC.QByteArray(datagram)
            stream = QC.QDataStream(data, QC.QIODevice.ReadWrite)
            stream.setVersion(QC.QDataStream.Qt_5_2)

            #print("S :", self.connectionAddress.index(host), stream.readUInt8(), stream.readUInt8(),  end = " ")

            stream.device().seek(0)

            if stream.readBool():
                player = self.connectionAddress.index(host)
                stream.writeUInt8(player)
                increment = stream.readUInt8()


                self.answer(host, increment)

                toSend= [True] * 6
                #print("M", host.toString(), increment, [(key.toString(), value) for key, value in self.players.items()])

                for key, value in self.players.items():
                    if value and key != host:
                        toSend[self.connectionAddress.index(key)] = False
                        self.udpSocket.writeDatagram(data, key, VOIP.PLAYERPORT)

                toSend.append(data)

                self.history[player].add(increment, toSend)

            else:
                playerR = self.connectionAddress.index(host)
                player = stream.readUInt8()
                increment = stream.readUInt8()

                #print("A", host.toString(), increment)

                self.history[player].setTrue(increment, playerR)


class GameSetUp:


    def __init__(self, server):
        self.f()
        self.pripojeni = [False for _ in range(6)]
        self.jmena= ["" for _ in range(6)]      # Zde jsou opravdová jména hráčů
        self.paraPocet = 6
        self.callback = server.sendMessage
        self.server = server
        self.zadavatel= 0
        self.jmenoServeru= "Unknown"


    def proved(self, h, nazev, args):
        self.zadavatel= h
        try:
            vysledek = self.funkce[nazev](args)
            if vysledek:
                if vysledek is True:
                    self.callback(h, nazev, args)
                else:
                    self.callback(h, *vysledek)
            else:
                self.callback(h, "chybna_akce", (h, nazev, ), (h, ))       #Je to vůbec potřeba?
        except Exception as e:
            self.callback(h, "chyba", (nazev, args), (h, ))
            #print ("SERVER: Error: ", e, "nazev: ", nazev, "( ", args, ")")

    def kontrola(self):
        for i, c in enumerate(self.server.connections):
            if not c:
                self.pripojeni[i] = False
                self.jmena[i] = ""

    def server_info(self, connection):
        self.server.writeReply(connection, "server_info", (self.jmenoServeru, self.pripojeni.count(True), False))

    def nove_spojeni(self, h):

        self.pripojeni[h] = True
        self.jmena[h] = "Player"
        self.server.updatePlayers(self.pripojeni)

        self.callback(h, "pripojen", (self.pripojeni, self.jmena, self.jmenoServeru), (h, ))
        self.callback(h, "nove_spojeni", ())


    def odpojeni_hrace(self, h):
        self.pripojeni[h] = False
        self.callback(h, "odpojeni_hrace", ((h, ), ))


    def zmen_jmeno(self, argumenty):
        jmeno= argumenty[0]
        if jmeno in self.jmena:
            for i in ("(1)", "(2)", "(3)", "(4)", "(5)"):
                if jmeno+i in self.jmena: continue
                jmeno+= i
                break
        self.jmena[self.zadavatel] = jmeno
        return ("zmen_jmeno", (jmeno, ))

    def jmeno_serveru(self, argumenty):
        if self.zadavatel == 0: #To by měl být admin
            self.jmenoServeru = argumenty[0]
            return True

    def spust_hru(self, _):
        if self.zadavatel != 0: return
        self.callback(self.zadavatel, "spust_hru", ())
        pripojeni = [i for i,p in enumerate(self.pripojeni) if p]
        jmena = [j for j in self.jmena if j]

        for i in range(6):
            if i < len(pripojeni): self.pripojeni[i] = True
            else: self.pripojeni[i] = False
        for i in range(6):
            if i < len(jmena): self.pripojeni[i] = jmena[i]
            else: self.pripojeni[i] = ""

        self.server.runGame(pripojeni, jmena, self.jmenoServeru)

    def f(self):
        self.funkce= {
            "spust_hru": self.spust_hru,
            "jmeno_serveru": self.jmeno_serveru,
            "zmen_jmeno": self.zmen_jmeno,
            #"spojeno": self.spojeno,
        }

class Game:

    KRYTI = 7 * 1000
    KOLO = 102 * 1000

    def __init__(self, server):
        self.f()
        self.ocekavam = ()
        self.pr_argumenty = []
        self.hraje = -1
        self.parazKolo = [0, False]
        self.ukoncil = False
        self.tahy = 0
        self.callback = server.sendMessage
        self.zadavatel= 0
        self.server= server
        self.pristiKolo= 0
        self.posledniAkce = ""

        self.odpocetKola= QC.QTimer()
        self.odpocetKola.setInterval(Game.KOLO)
        self.odpocetKola.timeout.connect(self.konec_kola)

        self.odpocetKryti= QC.QTimer()
        self.odpocetKryti.setInterval(Game.KRYTI)
        self.odpocetKryti.timeout.connect(self.konec_kryti)
        self.odpocetKryti.setSingleShot(True)

    def proved(self, h, nazev, args):
        """
        :param h: index hrace
        :param nazev: nazev prikazu
        :param args: arguemnty prikazu
        :return: None
        vybere správnou metodu ze slovníku funkce a zavolá ji s argumenty "args"
        """
        if self.ocekavam:
            if not nazev in self.ocekavam[0]: return            #Tohle jsem neočekával
        elif h != self.hraje: return                            #Příkaz přišel od hráče, který není na tahu
        self.zadavatel= h

        try:
            vysledek = self.funkce[nazev](args)
            if vysledek:
                if vysledek is True:
                    self.callback(h, nazev, args)
                else:
                    self.callback(h, *vysledek)
            else:
                self.callback(h, "chybna_akce", (nazev, self.tahy), (h, ))       #Je to vůbec potřeba?
        except Exception as e:
            pass
            #print ("ServerError: ", e, nazev, args, )

    def server_info(self, connection):
        self.server.writeReply(connection, "server_info", (self.jmenoServeru, self.pripojeni.count(True), True))

    def nove_spojeni(self, h):
        """
        oznámí všem hráčům, že se připojil nový klient, přidá ho do seznamu připojených a odešle mu všechny informace o stavu hry
        """

        #print("SERVER:  NOVE SPOJENI")
        self.pripojeni[h] = True
        self.callback(h, "pripojeni_hrace", ())

        try: pmistnost = self.mapa.zasobnikmapy[-1]
        except IndexError: pmistnost = None
        self.callback(0, "priprava_mapy", (pmistnost, len(self.mapa.zasobnikpredmetu), self.mapa.mapakaret, 6, self.mapa.paraziti, len(self.mapa.hraci)), (h,))
        self.callback(0, "priprava_hrace", (h, self.hra.hraci[0].predmety, self.hra.hraci[h].krve, self.mapa.nakazeni[h]), (h, ))
        self.callback(0, "priprava_hracu", ([h.me() for h in self.hra.hraci], ), (h, ))
        self.callback(0, "priprava_kola", (self.hraje, self.parazKolo[0], len(self.mapa.zasobnikmapy), len(self.mapa.zasobnikpredmetu), self.mapa.otevrenedvere, self.tahy), (h, ))


    def odpojeni_hrace(self, h):
        """
        oznámí všem hráčům odpojení klienta
        """
        self.pripojeni[h] = False
        self.callback(h, "odpojeni_hrace", (h, ))

    def priprav_hru(self, hraci, jmena, jmeno):

        self.jmenoServeru = jmeno
        self.pripojeni= [True for _ in hraci]
        self.server.updatePlayers([False for _ in hraci])

        self.mapa = ServerControl.Mapa(hraci, jmena, 6)
        self.hra = ServerControl.Hra(self.mapa)

        #print ("SERVER: PRIPRAVUJI HRU")

        # Odesílám data o mapě
        self.callback(0, "priprava_mapy", (self.mapa.zasobnikmapy[-1], len(self.mapa.zasobnikpredmetu), self.mapa.mapakaret, 6, self.mapa.paraziti, len(self.mapa.hraci)))
        # Odesílám hráčům jejich karty
        for i in range(len(hraci)):
            self.callback(0, "priprava_hrace", (i, self.hra.hraci[i].predmety, self.hra.hraci[i].krve, self.mapa.nakazeni[i]), (i, ))
        # Odesílám data o všech hráčích
        self.callback(0, "priprava_hracu", ([h.me() for h in self.hra.hraci], ))
        # Odesílám doplňující data
        self.callback(0, "priprava_kola", (self.hraje, self.parazKolo[0], len(self.mapa.zasobnikmapy), len(self.mapa.zasobnikpredmetu), self.mapa.otevrenedvere, self.tahy))


        QC.QTimer.singleShot(1000, self.nove_kolo)


    def pohyb_hrace(self, argumenty):
        if not(self.tahy or self.posledniAkce == "Speed") or not self.mapa.hraci[self.zadavatel].zivoty[argumenty[0]]: return
        vysledek = self.mapa.pohyb_hrace(self.zadavatel, *argumenty)
        if vysledek is None: return

        if self.posledniAkce == "Speed": tah = 0
        else: tah = 1
        self.tahy -=tah
        self.posledniAkce = ""
        if vysledek:
            udalost, setkani = vysledek
            if udalost == "Speed": self.posledniAkce = "Speed"
            elif udalost: self.callback(self.zadavatel, *vysledek[0])
            # ---
            if setkani:
                self.ocekavam = (("vymen_kartu", "strelba", "bodnuti"), self.hraje)
                self.server.updatePlayers(self.mapa.hraci_v_mistnosti(self.zadavatel))
        return ("pohyb_hrace", argumenty + (tah,) )

    def prohledat_mistnost(self, argumenty):
        """
        :param argumenty: clovek, jmT, clovekT
        """
        if not self.tahy or not self.mapa.hraci[self.zadavatel].zivoty[argumenty[0]]: return
        clovek, jmT, clovekT = argumenty
        vysledek = self.mapa.prohledat_mistnost(self.zadavatel, clovek, jmT, clovekT)
        if vysledek is None: return
        if vysledek is False: return ("dosly_karty", ())
        udalost, udalosti, karty = vysledek   #Vyvolal jsem parazita?
        self.posledniAkce = ""
        self.callback(self.zadavatel, udalost[0], udalost[1])
        for u in udalosti: self.callback(self.zadavatel, *u)
        self.tahy -=1
        if len(karty) == 2:
            self.callback(self.zadavatel, "lizani_karet", (jmT, clovekT, 0, karty[1]), (jmT, ), -1)
            return ("lizani_karet", (self.zadavatel, clovek, 1, karty[0]), (self.hraje, ), -1)
        elif len(karty) == 3:
            self.callback(self.zadavatel, "lizani_karet", (self.hraje, clovek, 0, karty[1]), (self.hraje, ), -1)           #Vracím karty na přeskáčku, protože se pak nemusím zabývat případem,
            self.callback(self.zadavatel, "lizani_karet", (self.hraje, clovek, 0, karty[2]), (self.hraje, ), -1)           # že se ihráč lízne pouze jednu kartu :)
        return ("lizani_karet", (self.hraje, clovek, 1, karty[0]), (self.hraje, ), -1)

    def objevit_mistnost(self, argumenty):      #("objevit_mistnost", (jmeno, pohyb, prevratit)
        if not self.tahy or not self.mapa.hraci[self.zadavatel].zivoty[argumenty[0]]: return
        vysledek = self.mapa.objevit_mistnost(self.zadavatel, *argumenty)
        if vysledek:
            self.posledniAkce = ""
            self.tahy -=1
            if vysledek[1] == 18:       #Objevil hnízdo parazitů (index 18)
                self.callback(self.zadavatel, "plosny_scan", (argumenty[0], self.mapa.nakazeni.count(True)))
            return ("objevit_mistnost", vysledek)

    def vymen_kartu(self, argumenty):
        if self.ocekavam[0][0] != "vymen_kartu": return
        karta = argumenty[0]
        if "Blood{0:d}".format(self.zadavatel) == karta and not self.mapa.nakazeni[self.zadavatel]: return  #Pokud dávám nákazu, musím být nakažený
        if not self.mapa.hraci[self.zadavatel].ma_predmet(karta): return    # Musí mít tu kartu

        if self.ocekavam[1] == self.hraje == self.zadavatel:    # karta hráče na tahu
            clovek, jmT, clovekT = argumenty[1], argumenty[2], argumenty[3]
            if not self.mapa.hraci[self.zadavatel].pos[clovek] == self.mapa.hraci[jmT].pos[clovekT]: return       # Musí být spolu v místnosti
            self.ocekavam = (("vymen_kartu", ), jmT)
            self.pr_argumenty = [karta, self.zadavatel, jmT]
            return ("vymen_kartu", (clovek, jmT, clovekT))
        elif self.ocekavam[1] == self.zadavatel:                       # karta cílového hráče
            nakazeny = self.hra.vymen_kartu(karta, *self.pr_argumenty)            # Provedu změny ve hře
            karta2 = self.pr_argumenty[0]
            self.ocekavam = ()
            self.pr_argumenty = []
            if not self.odpocetKola.isActive():
                self.callback(self.zadavatel, "vymena_karet", (karta, karta2, nakazeny), (self.hraje, self.zadavatel))
                self.konec_kola()
                return
            return ("vymena_karet", (karta, karta2, nakazeny), (self.hraje, self.zadavatel))


    def strelba(self, argumenty):       #('strelba', (jmT, clovekT, pohyb= False))
        if not self.tahy or not self.mapa.hraci[self.zadavatel].zivoty[0]: return
        # Můžu vytřelit do hráče vícekrát, pokud ještě nezahrál vestu
        if self.pr_argumenty and (self.pr_argumenty[2] != argumenty[0] or self.pr_argumenty[3] != argumenty[1]): return
        # Při vstoupení do místnosti nemůžu střílet do vedlejší místnosti nebo na parazita
        if self.ocekavam and (argumenty[2][0] or argumenty[2][1] or argumenty[1] is None): return
        if self.ocekavam and self.ocekavam[0][0] == "vymen_kartu": self.ocekavam = ()
        zraneni = self.hra.strelba(self.zadavatel, *argumenty)
        if not zraneni: return
        self.posledniAkce = ""
        self.tahy -=1
        args = (zraneni, )+ argumenty
        #print ("a", args)
        if argumenty[1] is None: return ("strelba", args)    #Střílím na parazita
        if self.pr_argumenty:
            self.pr_argumenty[-1] += zraneni
        else:
            self.ocekavam = (("kryti_vestou", "strelba"), (argumenty[0], ))  #Je to hráč
            self.pr_argumenty = ["hrac_utoci", self.zadavatel, argumenty[0], argumenty[1], zraneni]
        self.odpocetKryti.start()
        return ("strelba", args)

    def bodnuti(self, argumenty):
        """
        :param argumenty: jmT, clovekT
        :return:
        """
        if not self.tahy or not self.mapa.hraci[self.zadavatel].zivoty[1]: return
        vysledek = self.hra.bodnuti(self.zadavatel, *argumenty)
        if vysledek is None: return
        self.posledniAkce = ""
        self.tahy -=1
        if self.ocekavam: self.ocekavam = ()
        if not self.odpocetKola.isActive():
            self.callback(self.zadavatel, "bodnuti", (vysledek,) + argumenty)
            self.konec_kola()
            return
        return ("bodnuti", (vysledek,) + argumenty)

    def granat(self, argumenty):        #('granat', (ind, pohyb))
        """
        :param argumenty: int(ind), tuple(pohyb)
        :return: argumenty + tuple (zasahnuti paraziti, zasahnuti hraci)
        """
        if not self.tahy or not self.mapa.hraci[self.zadavatel].zivoty[argumenty[0]]: return
        if self.mapa.hraci[self.zadavatel].karty() < 6: return
        if self.hra.granat(self.zadavatel, *argumenty):
            self.posledniAkce = ""
            self.tahy -=1
            return True

    def energit(self, argumenty):
        #print(self.mapa.hraci[self.zadavatel].ma_predmet("EnergyDrink"), self.mapa.hraci[self.zadavatel].me()[2])
        if self.mapa.hraci[self.zadavatel].karty() < 6: return
        if self.mapa.hraci[self.zadavatel].spravuj_predmet("EnergyDrink", -1):
            self.tahy += 2
            return True

    def spawn(self, argumenty):
        self.server.updatePlayers(self.mapa.hraci_v_mistnosti(self.zadavatel))
        return self.mapa.hraci[self.zadavatel].spawn()

    def zvys(self, jm):
        """
        :param jm: int(index hráče)
        :return: vrací index hráče, který má hrát příští kolo
        """
        #Zkontroluji jestli nevyhráli nakažení!

        for n, h in zip(self.mapa.nakazeni, self.mapa.hraci):
            if (h.zivoty[1] > 0) and not n: break
        else:
            self.callback(0, "konec", (True, self.mapa.nakazeni))
            self.odpocetKola.stop()
            self.server.closeGame()
            return

        while True:     #Ten kdo je mrtvý nemůže hrát
            if jm == (len(self.mapa.hraci) - 1):
                jm = 0
            else:
                jm+= 1
            if self.mapa.hraci[jm].nazivu(): break
        return jm

    def konec_kryti(self):
        """
        V "self.pr_argumenty" se nacházejí dva typy krytí:
        A) ["hrac_utoci", jm, jmT, clovekT, zraneni]
        B) ["paraziti_utoci", [[int, int], [int, int], ...], hracNaTahu]
        """
        #print(self.pr_argumenty)
        nazev = self.pr_argumenty[0]
        #self.callback(0, "konec_kryti", ())
        if self.pr_argumenty[0] == "hrac_utoci":
            #print(self.pr_argumenty)
            _, _, jmT, clovekT, poskozeni = self.pr_argumenty
            self.mapa.hraci[jmT].zranit(poskozeni, clovekT)
            argumenty = tuple(self.pr_argumenty[1:])
        elif self.pr_argumenty[0] == "paraziti_utoci":
            for i, p in enumerate(self.pr_argumenty[1]):
                self.mapa.hraci[i].zranit(p[0], 0)
                self.mapa.hraci[i].zranit(p[1], 1)
            self.pristiKolo = self.zvys(self.pr_argumenty[2])
            if self.pristiKolo is None: return      # Když skončí hra
            self.parazKolo[0]= self.zvys(self.parazKolo[0])
            argumenty = (self.pr_argumenty[1], self.parazKolo[0])

        self.pr_argumenty = []
        self.callback(0, nazev, argumenty)
        self.ocekavam = ()
        if not self.odpocetKola.isActive():
            self.konec_kola()

    def kryti_vestou(self, argumenty):  # !!!
        """
        Sníží poškození udělené hráčům, pokud použijí vestu
        """
        if self.mapa.hraci[self.zadavatel].karty() < 6: return
        ind = argumenty[0]
        if self.pr_argumenty[0] == "hrac_utoci":           #["hrac_utoci", jmT, clovekT, poskozeni]
            if self.zadavatel != self.pr_argumenty[2]: return
            if self.pr_argumenty[4] < 1: return
            if self.mapa.hraci[self.zadavatel].spravuj_predmet("Vest", -1):
                self.pr_argumenty[4] -=1
                return True
        elif self.pr_argumenty[0] == "paraziti_utoci":     #["paraziti_utoci"] + [[dmg, dmg] _ for i in range(len(hraci))]
            if self.pr_argumenty[1][self.zadavatel][ind] < 1: return
            if self.mapa.hraci[self.zadavatel].spravuj_predmet("Vest", -1):
                self.pr_argumenty[1][self.zadavatel][ind] -=1
                return True

    def scan(self, args):
        """
        Vrátí seznam předmětů v ruce spoluhráče
        :param args: clovek, jmT, clovekT
        """
        if not self.tahy or not self.mapa.hraci[self.zadavatel].zivoty[args[0]]: return
        if self.mapa.hraci[self.zadavatel].karty() < 6: return
        vysledek = self.hra.scan(self.zadavatel, *args)
        if vysledek:
            self.posledniAkce = ""
            self.tahy -=1
            return ("scan", args + vysledek , (self.zadavatel, ), -2)

    def plosny_scan(self, args):
        # Viz ServerControl.Hra.plosny_scan
        if not self.tahy or not self.mapa.hraci[self.zadavatel].zivoty[args[0]]: return
        vysledek = self.hra.plosny_scan(self.zadavatel, args[0])
        if not vysledek: return
        self.posledniAkce = ""
        udalost, pocet = vysledek
        self.callback(self.zadavatel, *udalost)
        self.tahy -=1
        return ("plosny_scan", (args[0], pocet))

    def otevri_dvere(self, args):
        if not self.tahy or not self.mapa.hraci[self.zadavatel].zivoty[args[0]]: return
        udalost = self.hra.otevri_dvere(self.zadavatel, args[0])
        if not udalost: return
        self.posledniAkce = ""
        self.callback(self.zadavatel, *udalost)
        self.tahy -=1
        return True

    def vyloz_kartu(self, args):
        if self.mapa.hraci[self.zadavatel].karty() < 6: return
        return self.mapa.hraci[self.zadavatel].vyloz_predmet(args[0])

    def vypal_hnizdo(self, args):
        if self.tahy and self.mapa.hraci[self.zadavatel].zivoty[1]:
            if not self.hra.vypal_hnizdo(self.zadavatel): return
            self.callback(self.zadavatel, "konec", (False, self.mapa.nakazeni))
            self.odpocetKola.stop()
            self.server.closeGame()

    def vylecit_nem(self, args):
        if not self.tahy: return
        clovek, h = args   # To asi vysvtěluje dost
        hrac = self.mapa.hraci[self.zadavatel]
        y, x = hrac.pos[clovek]
        if self.mapa.mapakaret[y][x][0] != "FirstAid" and (hrac.zivoty[clovek] + h > 4): return
        hrac.zivoty[clovek] += h
        return True

    def vylecit_kar(self, args):
        if self.mapa.hraci[self.zadavatel].karty() < 6: return
        return self.mapa.hraci[self.zadavatel].vylecit(*args)

    def konec_kola(self, args= None):
        """
        Zjistím kdo hraje jako další, pohnu parazity pokud je potřeba
        """
        if self.ocekavam: return
        hraje = self.hraje
        self.hraje = -1
        self.callback(0, "konec_kola", ())
        if self.parazKolo[0] == self.pristiKolo and self.parazKolo[1]:
            self.parazKolo[1] = False
            pohyb = [0, 0]
            pohyb[randint(0, 1)] = choice([1, -1])
            zraneni = self.mapa.pohyb_parazitu(pohyb)
            self.callback(0, "pohyb_parazitu", (pohyb, zraneni))
            if zraneni:
                self.pr_argumenty = ["paraziti_utoci", zraneni, hraje]
                self.ocekavam= (("kryti_vestou", ), )
                self.odpocetKryti.start()
                QC.QTimer.singleShot(Game.KRYTI + 1000, self.nove_kolo)
            else:
                self.pristiKolo = self.zvys(hraje)
                if self.pristiKolo is None: return      # Když skončí hra
                self.parazKolo[0] = self.zvys(self.parazKolo[0])
                self.callback(0, "paraziti_utoci", (zraneni, self.parazKolo[0]))
                self.nove_kolo()
        else:
            if not self.parazKolo[1]:
                self.parazKolo[1] = True
            self.pristiKolo = self.zvys(hraje)
            if self.pristiKolo is None: return      # Když skončí hra
            self.nove_kolo()

    def nove_kolo(self, args= None):
        if self.pristiKolo is None: return          # Hra už skončila, ale některé timery ještě nedoběhli
        self.hraje= self.pristiKolo
        #print ("NOVE KOLO", self.hraje, self.mapa.hraci)
        if self.mapa.otevrenedvere == self.hraje: self.mapa.otevrenedvere = -1
        self.tahy = self.mapa.hraci[self.hraje].tahy()
        self.callback(0, "nove_kolo", (self.hraje, ))
        self.odpocetKola.start()

    def konec(self):
        pass

    def f(self):
        self.funkce= {
            "pohyb_hrace": self.pohyb_hrace,
            "prohledat_mistnost": self.prohledat_mistnost,
            "objevit_mistnost": self.objevit_mistnost,
            "vymen_kartu": self.vymen_kartu,
            "strelba": self.strelba,
            "bodnuti": self.bodnuti,
            "granat": self.granat,
            "vylecit_nem": self.vylecit_nem,
            "vylecit_kar": self.vylecit_kar,
            "energit": self.energit,
            "kryti_vestou": self.kryti_vestou,
            "konec_kola": self.konec_kola,
            #"nove_kolo": self.nove_kolo,
            "spawn": self.spawn,
            "scan": self.scan,
            "plosny_scan": self.plosny_scan,
            "otevri_dvere": self.otevri_dvere,
            "vypal_hnizdo": self.vypal_hnizdo,
            "vyloz_kartu": self.vyloz_kartu,
        }


def run(show = True):
    app = QW.QApplication(sys.argv)
    server = ServerDlg()
    voip = VOIP(server)
    voip.players = server.players
    voip.connectionAddress = server.connectionAddress
    gameSetUp = GameSetUp(server)
    server.setup(gameSetUp)
    if show: server.show()
    server.move(0, 0)
    app.exec_()

if __name__ == "__main__":
    run()