__author__ = 'Josef'
# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtCore as QC
from PyQt5 import QtGui as QG
from PyQt5 import QtWidgets as QW
from PyQt5 import QtNetwork as QN
from PyQt5.QtQuick import QQuickItem
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from random import randint
import numpy as np
import pyaudio
import win_unicode_console

from ast import literal_eval

from store import Sequence


PORTS = (9998, 9999)
PORT = 9999
SIZEOF_UINT32 = 4

win_unicode_console.enable()



class Client(QC.QObject):

    command = pyqtSignal(int, str, tuple)
    closed = pyqtSignal()

    def __init__(self, parent=None):
        super(Client, self).__init__(parent)

        # Ititialize socket
        self.socket = QN.QTcpSocket()


        # Initialize data IO variables
        self.nextBlockSize = 0
        self.request = None

        #self.setWindowTitle("Client")
        # Signals and slots for networking
        self.socket.readyRead.connect(self.readFromServer)
        self.socket.disconnected.connect(self.serverHasStopped)
        self.socket.error.connect(self.serverHasError)

    # Update GUI
    def updateUi(self):
        pass
    # Create connection to server
    def connectToServer(self, address):
        self.socket.connectToHost(address, PORT)

    def disconnect(self):
        self.socket.disconnectFromHost()

    def sendMessage(self, nazev, argumenty):
        self.request = QC.QByteArray()
        stream = QC.QDataStream(self.request, QC.QIODevice.WriteOnly)
        stream.setVersion(QC.QDataStream.Qt_4_2)
        stream.writeUInt32(0)
        stream.writeQString(nazev)
        stream.writeQString(str(argumenty))
        stream.device().seek(0)
        stream.writeUInt32(self.request.size() - SIZEOF_UINT32)
        self.socket.write(self.request)
        self.nextBlockSize = 0
        self.request = None

    def readFromServer(self):
        stream = QC.QDataStream(self.socket)
        stream.setVersion(QC.QDataStream.Qt_5_2)

        while True:
            if self.nextBlockSize == 0:
                if self.socket.bytesAvailable() < SIZEOF_UINT32:
                    return
                self.nextBlockSize = stream.readUInt32()
            if self.socket.bytesAvailable() < self.nextBlockSize:
                return
            h, nazev, argumenty= stream.readUInt32(), stream.readQString(), stream.readQString()
            #print ("KLIENT: přišli data: ", (h, nazev), argumenty)
            self.nextBlockSize = 0
            self.command.emit(h, nazev, literal_eval(argumenty))

    def serverHasStopped(self):
        #self.socket.close()
        self.socket.disconnectFromHost()
        self.closed.emit()

    def serverHasError(self):
        self.socket.close()

class NetworkScan(QC.QObject):

    addServer = pyqtSignal(int, str, str, int, bool)
    removeServer = pyqtSignal(int)

    def __init__(self):
        super(NetworkScan, self).__init__(None)


    def run(self):
        self.socket = QN.QTcpSocket()

        self.currentIP = 0
        self.mask = None

        self.serverList = []

        self.socket.hostFound.connect(self.serverFound)

        self.nextBlockSize = 0

        self.go = True
        while self.go:
            self.connectToServer()
            if self.socket.waitForConnected(100):
                #print("I SMELL SMTHING")
                self.socket.waitForReadyRead(1000)
                self.readFromServer()
            elif self.address in self.serverList:
                i = self.serverList.index(self.address)
                del self.serverList[i]
                self.removeServer.emit(i)

    def close(self):
        self.go = False
        self.socket.close()

    # Připojení k serveru
    def connectToServer(self):

        if self.mask is None:
            for address in QN.QNetworkInterface.allAddresses():
                if address != QN.QHostAddress.LocalHost and address.toIPv4Address():
                    m = address.toString().split(".")[: -1]
                    if m[0] not in ("10", "172", "192"): continue
                    self.mask = ".".join(m)
                    #print ("FOUND", address.toString())
                    break
            else:
                self.address = QN.QHostAddress.LocalHost.toString()
                self.socket.connectToHost(self.address, PORT)
                return

        #self.address = "25.168.108.230"
        self.address = "{0:s}.{1:d}".format(self.mask, self.currentIP)


        if self.currentIP == 255:
            self.currentIP = 0
        else:
            self.currentIP += 1


        self.socket.connectToHost(self.address, PORT)


    def disconnect(self):
        self.socket.disconnectFromHost()

    def readFromServer(self):
        stream = QC.QDataStream(self.socket)
        stream.setVersion(QC.QDataStream.Qt_5_2)
        while True:
            if self.nextBlockSize == 0:
                if self.socket.bytesAvailable() < SIZEOF_UINT32:
                    continue
                self.nextBlockSize = stream.readUInt32()
            if self.socket.bytesAvailable() < self.nextBlockSize:
                continue
            h, nazev, argumenty= stream.readUInt32(), stream.readQString(), stream.readQString()
            #print ("SCAN: přišli data: ", (h, nazev), argumenty)
            self.nextBlockSize = 0

            if self.address in self.serverList:
                i = self.serverList.index(self.address)
            else:
                i = -1
                self.serverList.append(self.address)
            self.addServer.emit(i, self.address, *literal_eval(argumenty))
            self.disconnect()
            return

    def serverFound(self):
        pass##print("našel jsem ho")

    def serverHasStopped(self):
        self.socket.close()

    def serverHasError(self):
        self.socket.close()

class VOIP(QC.QObject):

    MYPORT = 9998
    SERVERPORT = 9997

    RINTERVAL = 100


    def __init__(self, server, parent= None):
        super(VOIP, self).__init__(parent)

        self.udpSocket = QN.QUdpSocket(self)
        self.udpSocket.bind(QN.QHostAddress("0.0.0.0"), VOIP.MYPORT)

        self.udpSocket.readyRead.connect(self.processPendingDatagrams)

        self.p = pyaudio.PyAudio()

        self.serverIP= server

        self.history = Sequence(True)

        self.resendTimer = QC.QTimer()
        self.resendTimer.setInterval(VOIP.RINTERVAL)
        self.resendTimer.timeout.connect(self.resendDatagram)
        self.resendTimer.start()


    def resendDatagram(self):
        return #Počkejte si na verzi 1.1
        for sent, request in self.history:
            if not sent:
                self.udpSocket.writeDatagram(request, QN.QHostAddress(self.serverIP), VOIP.SERVERPORT)

    def answer(self, player, number):
        request = QC.QByteArray()

        stream = QC.QDataStream(request, QC.QIODevice.WriteOnly)
        stream.setVersion(QC.QDataStream.Qt_5_2)
        stream.writeBool(False)
        stream.writeUInt8(player)
        stream.writeUInt8(number)

        self.udpSocket.writeDatagram(request, QN.QHostAddress(self.serverIP), VOIP.SERVERPORT)

    def writeDatagram(self, message, number):
        request = QC.QByteArray()

        stream = QC.QDataStream(request, QC.QIODevice.WriteOnly)
        stream.setVersion(QC.QDataStream.Qt_5_2)
        stream.writeBool(True)
        stream.writeUInt8(0)        # Vyhrazuji si místo pro odesílatele zprávy, toho zapíše server
        stream.writeUInt8(number)
        stream.writeBytes(message)

        #print("SEND", number)
        self.udpSocket.writeDatagram(request, QN.QHostAddress(self.serverIP), VOIP.SERVERPORT)
        self.history.add(number, [False, request])

    newMessage = pyqtSignal(int, int, bytes)
    def processPendingDatagrams(self):

        while self.udpSocket.hasPendingDatagrams():
            (data, port, adr) = self.udpSocket.readDatagram(self.udpSocket.pendingDatagramSize())

            stream = QC.QDataStream(QC.QByteArray(data))
            stream.setVersion(QC.QDataStream.Qt_5_2)

            if stream.readBool():
                player, index, chunk = stream.readUInt8(), stream.readUInt8(), stream.readBytes()

                self.answer(player, index)

                self.newMessage.emit(player, index, chunk)
            else:
                index = stream.readUInt8()

                self.history.setTrue(index)

    def close(self):
        self.udpSocket.close()




if __name__ == "__main__":
    #print (__name__)
    app = QW.QApplication(sys.argv)
    client = Client()
    client.show()
    app.exec_()

