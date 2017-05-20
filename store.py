__author__ = 'Anthony'
from PyQt5.QtCore import QMutex, QMutexLocker, QObject
from time import perf_counter

class Null:
    # Můj pomocník :)

    def __bool__(self): return False

    def __str__(self): return "NULL"

    def __int__(self): return 0

class Buffer(QObject):
    """
    Jde o jakýsi zásobník, který umisťuje příchozí prvky ne vždy nahoru (jako FIFO) ale řadí je podle incrementu (nejvyšší je nahoře).
    Pracuje stále se stejně velkým polem a jeho vrchol stanovuje podle indexu "readPointer"
    """

    LENGTH = 11     # Určuje jak moc velké bude zpoždění (zvuku)
    MARGIN = 1      # Určuje rezervu (když by se spozdilo čtení a já dostal další prvky)
    MAX = 255
    DELAY = 5       # Kolikrát za sebou je možné, aby AP nebyl na úrovni RP
    DEFAULT = Null()

    def __init__(self, parent = None):
        super().__init__(parent)

        self.readPointer = 0
        self.addPointer = 0
        self.increment = 0
        self.dcounter = Buffer.DELAY

        self.array = [Buffer.DEFAULT] * Buffer.LENGTH

        self.mutex = QMutex()   # Protože s ním pracuju v různých vláknech

    def increaseRP(self):
        self.readPointer += 1
        if self.readPointer == Buffer.LENGTH:
            self.readPointer = 0

    def increaseAP(self, difference):
        # Dělá vlastně nachlup to samé jako increaseRP, ale s předem daným rozdílem
        self.addPointer = (self.addPointer + difference) % Buffer.LENGTH

    def write(self, difference, sample):
        """
        Zapíše "sample" do seznamu podle "difference"
        """
        current = (self.addPointer + difference - Buffer.MARGIN - 1) % Buffer.LENGTH
        self.array[current] = sample
        # Ta jednička tam je protože pokud mi přišla následující stopa, musím ji logicky zapsat jako poslední od zadu (d = 1  ==>> 1 - 1 = 0 -> pak zvýším pointer)

    def get(self):
        """
        Vrátí poslední prvek, vymaže ho za sebou a posune pointer
        """
        locker = QMutexLocker(self.mutex)
        sample = self.array[self.readPointer]
        self.array[self.readPointer] = Buffer.DEFAULT
        self.increaseRP()

        return sample

    def add(self, index, sample):
        """
        Zařídí, aby se prvek opravdu zapsal podle indexu do pořadí, pokud je index moc nízký, tak není přijmut
        """
        locker = QMutexLocker(self.mutex)

        diff = index - self.increment


        ##print(index, self.readPointer, self.addPointer)
        #print(index, diff, self)

        if (self.readPointer - self.addPointer) % Buffer.LENGTH > 1:
            self.dcounter += 1
        else:
            self.dcounter = 0

        if self.dcounter == Buffer.DELAY:
            diff = Buffer.LENGTH *2
            self.dcounter = 0
        elif diff > Buffer.MAX / 2:     # Index má maximální velikost, a proto musím rozdíl spravně upravit, když mi například přijde 0 self.increment je MAX
            diff -= Buffer.MAX + 1
        elif -diff > Buffer.MAX / 2:
            diff += Buffer.MAX + 1

        if (Buffer.MARGIN - diff) > (self.addPointer - self.readPointer - 1) % Buffer.LENGTH: return    # Nesmí být příliš malý
        if (diff - Buffer.MARGIN) > (self.readPointer - self.addPointer) % Buffer.LENGTH:               # Když je moc velký, tak ho prostě zapíšu dopředu
            self.increaseAP(diff)
            self.increment = index
            self.readPointer = self.addPointer
            self.write(0, sample)
        elif diff > 0:
            self.write(diff, sample)
            if self.addPointer != self.readPointer:     # Pokud se neaplikuje margin
                self.increaseAP(diff)
                self.increment = index
        else:
            self.write(diff, sample)

    def __bool__(self):
        return self.array[self.readPointer] is not Buffer.DEFAULT

    def __str__(self):
        a = [i is not Buffer.DEFAULT and "OOO" or "---" for i in self.array]
        a[self.addPointer] = "A" + "".join(list(a[self.addPointer])[1:])
        a[self.readPointer] = "".join(list(a[self.readPointer])[:-1]) + "R"
        return str(a)

class Sequence:

    LENGTH = 11
    MS = 23

    DMAX = 9 * MS
    DMIN = 5  * MS

    MAX = 255
    DEFAULT = Null

    def __init__(self, show = False):

        self.show = show
        self.time = 0
        self.pointer = 0
        self.increment = 0

        self.array = [Sequence.DEFAULT] * Sequence.LENGTH


    def increasePointer(self, difference):
        for i in range(difference):
            current = (self.pointer + i) % Sequence.LENGTH
            self.array[current] = Sequence.DEFAULT
        self.pointer = (current + i + 1) % Sequence.LENGTH

    def clear(self):
        for i in range(Sequence.LENGTH):
            self.array[i] = Sequence.DEFAULT


    def write(self, difference, sample):
        i = (self.pointer + difference - 2) % Sequence.LENGTH
        self.array[i] = sample
        # 2 protože jsem už posunul pointer dopředu

    def setTrue(self, index, pos = 0):
        i = (self.pointer + index - self.increment - 1) % Sequence.LENGTH
        #if self.show: #print(index, self.pointer, " => ",i, perf_counter())
        if self.array[i] is not Sequence.DEFAULT:
            self.array[i][pos] = True

    def add(self, index, stream):
        """
        Zařídí, aby se prvek opravdu zapsal podle indexu do pořadí, pokud je index moc nízký, tak není přijmut
        """
        #if self.show: #print(index, (perf_counter() - self.time) * 1000)
        if perf_counter() - self.time > Sequence.DMAX / 1000:
            #if self.show: print("this", perf_counter() - self.time, perf_counter())
            self.time = perf_counter()
            self.clear()

            self.array[0] = stream
            self.pointer = 0
            self.increment = index
            return
        self.time = perf_counter()


        diff = index - self.increment

        #if self.show: #print(stream)
        #if self.show: #print(index, diff, self.increment, self.pointer, perf_counter())

        if diff > Buffer.MAX / 2:     # Index má maximální velikost, a proto musím rozdíl spravně upravit (0 - 255)
            diff -= Buffer.MAX + 1
        elif -diff > Buffer.MAX / 2:
            diff += Buffer.MAX + 1

        if diff < -Sequence.LENGTH:
            #print("before")
            self.clear()
            diff = 0
        elif diff > Sequence.LENGTH:
            #print("after")
            self.clear()
            diff = 0

        if diff > 0:
            self.increasePointer(diff)
            self.write(diff, stream)
            self.increment = index
        else:
            self.write(diff, stream)

    def __iter__(self):
        """
        Vrátí seznam všech zpráv v časovém intervalu  DMIN < ... < DMAX
        """
        array = []
        time = perf_counter()
        for i in range(Sequence.LENGTH):
            if time - ( self.time - (i * Sequence.MS / 1000) ) > Sequence.DMAX / 1000: break
            elif time - ( self.time - (i * Sequence.MS / 1000) ) < Sequence.DMIN / 1000: continue

            current = self.array[self.pointer - i - 1]
            if current is not Sequence.DEFAULT: array.append(current)

        #if self.show: #print(self)
        return iter(array)

    def __str__(self):
        a = [i is not Sequence.DEFAULT and i[:-1] or " Null " for i in self.array]
        return str(a)
