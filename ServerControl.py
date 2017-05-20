# -*- coding: utf-8 -*-
__author__ = 'Josef'

from random import shuffle, randint, choice

class Items:
    ROOMS= (
            ["FirstAid", (2, 0, 0, 0), True, "room12"],     # Léčení
            ["Storage", (0, 1, 1, 0), True, "room0"],       # Lížeš tři karty
            ["Storage", (1, 1, 0, 1), True, "room5"],
            ["Stock", (2, 0, 1, 0), True, "room2"],         # Dva hráči lízají jednu kartu
            ["Stock", (1, 0, 0, 1), True, "room3"],
            ["Stock", (0, 1, 1, 0), True, "room4"],
            ["Stock", (1, 1, 0, 2), True, "room7"],
            ["Parasite", (1, 0, 0, 1), True, "room9"],      # Při vstupu vyvoláš parazita
            ["Parasite", (1, 1, 1, 0), True, "room15"],
            ["Parasite", (1, 1, 0, 1), True, "room16"],
            ["Parasite", (0, 1, 1, 1), True, "room17"],
            ["Speed", (2, 0, 0, 1), True, "room1"],         # Procházíš bez akce
            ["Speed", (1, 1, 1, 1), True, "room6"],
            ["Speed", (1, 1, 1, 1), True, "room11"],
            ["Terminal2", (2, 0, 0, 0), True, "room8"],     # PC ve dvojité místnosti
            ["Empty", (2, 2, 1, 1), None, "room13"],        # Prostě prázdná
            ["Empty", (0, 1, 1, 1), None, "room14"],
            ["Terminal", (0, 1, 1, 1), True, "pc"],         # PC - scan/ dveře
            ["Nest", (0, 0, 1, 0), None, "nest"],           # To vypal
            ["Reactor", (1, 1, 1, 1), None, "reactor"],     # Tady to vše začalo
            # Reálně je pak ještě vždy na konci přidáno False, což značí, že místnost není otočená
    )

    CARDS= {"FirstAid": 3,
            "Scanner": 1,
            "Ammo": 4,
            "Grenade": 2,
            "Scope": 2,
            "Riffle": 2,
            "Vest": 8,
            "Gas": 16,
            "Infection": 1,
            "Card": 2,
            "EnergyDrink": 2,
            "Knife": 3,
            "Parasite": 5
    }

    def __init__(self):
        pass

class Mapa:
    Y = 25
    X = 27
    def __init__(self, avatary, jmena, parazitimax):
        self.mapakaret = [[None for y in range(Mapa.Y)] for i in range(Mapa.X)]     #Hrací plocha
        self.mapakaret[int(Mapa.Y/2)][int(Mapa.X/2)] = Items.ROOMS[-1][:]  + [False]    #Doprostřed umístím Reaktor

        self.zasobnikmapy = []
        self.zasobnikpredmetu = []
        self.priprav_balicky(len(jmena))

        self.otevrenedvere = -1
        self.parazitimax = parazitimax
        self.smery = ((0, 2), (1, 3))
        self.paraziti= []
        self.hraci= []
        self.nakazeni = [False for _ in range(len(jmena))]              # Kteří hráči jsou nakažení
        for i in range(len(avatary)):         #Inicialuziju hráče
            h= Hrac(jmena[i], avatary[i])
            for _ in range(2):
                predmet = self.zasobnikpredmetu.pop()
                h.spravuj_predmet(self.nakaza(i, predmet), 1)   #Dám jim karty
            self.hraci.append(h)

    def priprav_balicky(self, pHracu):
        """
        :param pHracu: počet hráčů

        Předpřipraví bálíčky karet předmětů a karet mapy
        """
        zasobnikMapy = list(range(len(Items.ROOMS) - 3))
        shuffle(zasobnikMapy)
        posledni = [zasobnikMapy.pop(), len(Items.ROOMS) - 2, len(Items.ROOMS) - 3]
        shuffle(posledni)
        self.zasobnikmapy = posledni + zasobnikMapy

        zasobnikPredmetu = []
        for k, v in Items.CARDS.items():
            if k == "Gas": v -= pHracu
            elif k == "Infection": continue
            elif k == "Parasite": continue
            for _ in range(v):
                zasobnikPredmetu.append(k)
        shuffle(zasobnikPredmetu)
        hore =  ["Gas" for _ in range(pHracu * 2)] + ["Infection"]
        shuffle(hore)
        dole = zasobnikPredmetu[: -pHracu*2] + (["Parasite"] * Items.CARDS["Parasite"])
        shuffle(dole)
        self.zasobnikpredmetu = dole + hore

    def nakaza(self, jm, predmet):
        if predmet == "Infection": self.nakazeni[jm] = True
        return predmet

    def pohyb_hrace(self, jm, clovek, pohyb):
        """
        Pohyb ve skutečnosti udává směr pohybu
        Vrací: False = hráč se nemůže pohnout | None =  hráč se pohne, ale s nikým se nesetká | Tuple setkání
        """
        if self.kolize(jm, clovek, pohyb):
            return
        self.hraci[jm].pos[clovek][0] += pohyb[0]
        self.hraci[jm].pos[clovek][1] += pohyb[1]

        for i, h in enumerate(self.hraci):
            if jm != i and (self.hraci[jm].pos[clovek] == h.pos[0] or self.hraci[jm].pos[clovek] == h.pos[1]):
                setkani = True
                break
        else: setkani = False

        udalost = ()
        y, x= self.hraci[jm].pos[clovek]
        if self.mapakaret[y][x][0] == "Parasite":
            udalost = self.vyvolej_parazita(y, x)
        elif not setkani and self.mapakaret[y][x][0] == "Speed":
            udalost = "Speed"
        elif self.mapakaret[y][x][0] == "Reactor":
            setkani = False
        return udalost, setkani

    def hraci_v_mistnosti(self, jm):
        """
        Zjistí s kterými hráči se můžu bavit (VOIP).
        """
        pos = self.hraci[jm].pos
        setkani = []
        for i, h in enumerate(self.hraci):
            setkani.append(  (pos[0] in h.pos) or (pos[1] in h.pos)  )
        return setkani


    def pohyb_parazitu(self, pohyb):
        """
        POHNE všemi parazity ve zvoleném směru, pokud je to možné, a vyhodnotí poškození udělené hráčům
        :return:
        """
        y1, x1 = pohyb
        self.paraziti.sort()
        posledni = ()
        poskozeni = 0
        hraci= []       # Defakto seznam setkání hráčů
        pohnul = False
        vysledek = [ [0, 0] for _ in range(len(self.hraci))] #seznam hráčů s uděleným poškozením
        for i, p in enumerate(self.paraziti[:]):
            (y, x), count, type = p
            # Pokud jsem netáhl parazitem ve stejné místnosti
            if posledni != (y, x):
                posledni = (y, x)
                if not self.kolize(i, None, pohyb):
                    pohnul = True
                    self.paraziti[i][0][0] +=y1
                    self.paraziti[i][0][1] +=x1
                # Udílení zranění
                # Pokud narazím na místnost, kterou jsem ještě nevyhodnocoval, pak vyhodnotím staré poškození
                for (jm, clovek) in hraci:
                    vysledek[jm][clovek]+= poskozeni
                #Zjišťuji s kým se setkali
                poskozeni = count* (type == 2 and 2 or 1)
                hraci = []
                for i1, h in enumerate(self.hraci):
                    if self.paraziti[i][0] == h.pos[0]: hraci.append((i1, 0))
                    if self.paraziti[i][0] == h.pos[1]: hraci.append((i1, 1))
            else:   #Pokud jsem již táhnul s parazitem ve stejné místnosti
                poskozeni+= count* (type == 2 and 2 or 1)
                if pohnul:
                    self.paraziti[i][0][0] +=y1
                    self.paraziti[i][0][1] +=x1

        for (jm, clovek) in hraci:
            vysledek[jm][clovek]+= poskozeni

        #Kdyby bylo více parazitů se stejnými souřadnicemi v seznam parazitu, tak je dám k sobě dohromady
        paraziti= []
        for p in self.paraziti:
            for p1 in paraziti:
                if p1[0] == p[0] and p1[2] == p[2]:
                    p1[1] += p[1]
                    break
            else:
                paraziti.append(p)
        self.paraziti= paraziti

        if vysledek == [[0, 0] for _ in range(len(self.hraci))]:
            return []
        return vysledek

    def prohledat_mistnost(self, jm, ind, jmT, clovekT):
        """
        :param jm: index hráče
        :param ind: clovek|klon?
        :param jmT: index spoluhráče
        :return: tuple(zprava hráčům, předměty které si lízly)
        """
        y, x = self.hraci[jm].pos[ind]
        mistnost = self.mapakaret[y][x]
        predmety = []
        paraziti = []
        if mistnost[2] is None: #Místnost se nedá prohledat
            return
        try:
            if mistnost[0] == "Storage" and mistnost[2]:    #Bereš tři karty
                for _ in range(3):
                    p = self.zasobnikpredmetu.pop()
                    if p == "Parasite": paraziti.append(self.vyvolej_parazita(y, x))
                    else: self.hraci[jm].spravuj_predmet(self.nakaza(jm, p), 1)
                    predmety.append(p)
            elif mistnost[0] == "Stock":    #Dva hráči berou jednu kartu
                p = self.zasobnikpredmetu.pop()
                if p == "Parasite": paraziti.append(self.vyvolej_parazita(y, x))
                else: self.hraci[jm].spravuj_predmet(self.nakaza(jm, p), 1)
                predmety.append(p)
                if jmT != jm and [y, x] == self.hraci[jmT].pos[clovekT]:
                    p = self.zasobnikpredmetu.pop()
                    if p == "Parasite": paraziti.append(self.vyvolej_parazita(y, x))
                    else: self.hraci[jmT].spravuj_predmet(self.nakaza(jmT, p), 1)
                    predmety.append(p)
            else:   #Bereš jednu kartu
                p = self.zasobnikpredmetu.pop()
                if p == "Parasite": paraziti.append(self.vyvolej_parazita(y, x))
                else: self.hraci[jm].spravuj_predmet(self.nakaza(jm, p), 1)
                predmety.append(p)
        except IndexError:  #Když už nejsou žádné karty
            return False
        return (self.pouzij_mistnost(y, x), paraziti, predmety)

    def pouzij_mistnost(self, y, x):
        """
        Vyvolá parazita nebo otočí místnost
        """

        mistnost= self.mapakaret[y][x]
        if mistnost[2]:     #Měním status knihovny na prohledáno
            self.mapakaret[y][x][2] = False
            udalost = ("otoc_mistnost", (y, x))
        else:               #Vyvolávám parazita
            udalost = self.vyvolej_parazita(y, x)
        return udalost

    def vyvolej_parazita(self, y, x):
        """
        Přivolá parazita na mapu
        Pokud dojdou bílí, dávají se černí         vrátí: (None, [[y, x], poskozeni])
        Pokud dojdou černí, přitáhne se náhodný parazit z mapy      vrátí: (index, [y, x])
        """
        pohyb = choice([[0, 0], [0, 1], [1, 0], [-1, 0], [0, -1]])
        if self.mapakaret[y+pohyb[0]][x+pohyb[1]] is not None:  #Pokud ve směru přivolání je odkryta mapa
            y, x = (y+pohyb[0], x+pohyb[1])

        pocet = 0
        for p in self.paraziti:
            if p[2] == 0: pocet += p[1]
        if pocet > self.parazitimax:
            pocet = 0
            for p in self.paraziti: pocet += p[1]
            if pocet < self.parazitimax*2: #Kontroluji jestli je dostatek bílých a černých parazitů
                p = [[y, x], 2]
                self.pridej_parazita(*p)
                r = (None, p)
            else:
                index = randint(0, len(self.paraziti) -1)  #V případě nouze si ho přitáhnu odjinud
                souradnice = [y, x]
                self.pridej_parazita([y, x], self.paraziti[index][2])
                self.odeber_parazita(index)
                r = (index, souradnice)
        else:
            p = [[y, x], 0]
            self.pridej_parazita(*p)
            r = (None, p)
        return ("vyvolej_parazita", r)

    def pridej_parazita(self, souradnice, type):
        for i in range(len(self.paraziti)):
            if souradnice == self.paraziti[i][0] and type == self.paraziti[i][2]:
                self.paraziti[i][1]+= 1
                return
        self.paraziti.append([souradnice, 1, type])

    def odeber_parazita(self, index):
        if self.paraziti[index][1] == 1:
            del self.paraziti[index]
            return True
        else:
            self.paraziti[index][1] -=1
            return False

    def zranit_parazita(self, pozice, typ):
        for i, p in enumerate(self.paraziti):
            if p[0] == pozice and p[2] == typ: break
        else: return
        self.odeber_parazita(i)
        if p[2] == 2:
            self.pridej_parazita(p[0], 1)
            return False
        return True


    def vrat_smer(self, pohyb):
        if pohyb[0]:
            if pohyb[0] == 1: return (2, 0)
            if pohyb[0] == -1: return (0, 2)
        if pohyb[1]:
            if pohyb[1] == 1: return (1, 3)
            if pohyb[1] == -1: return (3, 1)

    def kolize(self, jm, clovek, pohyb):
        """
        Zjistí, zda je oblast průchozí v daném směru
        """
        (y1, x2) = pohyb
        if clovek is not None:
            (y, x) = self.hraci[jm].pos[clovek]
            karta = self.hraci[jm].vylozeno[1]
        else:
            y, x = self.paraziti[jm][0]
            karta= False

        smer = self.vrat_smer(pohyb)
        # Pokud tu není ještě objevená místnost
        if not self.mapakaret[y+y1][x+x2]: return True
        try: pruchod = (self.mapakaret[y][x][1][smer[0]], self.mapakaret[y+y1][x+x2][1][smer[1]])
        except TypeError: return True
        if pruchod[0] and pruchod[1]:
            #Když ve směru pohybu není stěna nebo prázdno
            if pruchod[0]== 1 and pruchod[1]== 1:
                #Pokud tam nejsou dveře
                return False
            else:
                #Pokud tam jsou dveře
                if karta or self.otevrenedvere> -1: return False
                else: return True
        return True

    def setkani(self, y, x, paraziti):
        """
        :param paraziti: mám vrátit i setkání s parazity?
        Vrátí seznam [(jm, clovek), (...), ...] clovek = None -> parazit
        """
        setkani = []
        for i, h in enumerate(self.hraci):
            if [y, x] == h.pos[0]: setkani.append((i, 0))
            if [y, x] == h.pos[1]: setkani.append((i, 1))

        if not paraziti: return setkani

        for i, p in enumerate(self.paraziti):
            if [y, x] == p[0]: setkani.append((i, None))

        return setkani

    def prevrat_mistnost(self, m):
        return (m[2], m[3], m[0], m[1])

    def objevit_mistnost(self, jm, clovek, pohyb, prevratit):
        """
        :param jmeno: tuple(ind hrace, klon|clovek)
        :param pohyb: tuple(smer objeveni)
        :param prevratit: int(1|0)
        :return: list (pristi karta mapy)
        """
        (y, x) = self.hraci[jm].pos[clovek]
        (y1, x1) = pohyb
        smer = self.vrat_smer(pohyb)
        # Pokud brání ve výhledu stěna NEBO je již místnost objevená NEBO v tomto směru není průchod do místnosti
        mistnost= prevratit and self.prevrat_mistnost(Items.ROOMS[self.zasobnikmapy[-1]][1]) or Items.ROOMS[self.zasobnikmapy[-1]][1]   #Převratím místnost, pokud je potřeba
        if not self.mapakaret[y][x][1][smer[0]] or self.mapakaret[y+y1][x+x1] or not mistnost[smer[1]]: return
        index= self.zasobnikmapy[-1]
        novamistnost = Items.ROOMS[self.zasobnikmapy.pop()][:]
        novamistnost[1]= mistnost
        self.mapakaret[y+y1][x+x1] = novamistnost + [prevratit]
        try:
            pmistnost= self.zasobnikmapy[-1]
        except IndexError:
            pmistnost = None

        return ((y+y1, x+x1), index, prevratit, pmistnost, jm, clovek)

    def __str__(self):
        text = ""
        for i in self.mapakaret:
            text += "%s\n" %i
        return text

class Hra:
    def __init__(self, mapa):
        self.mapa = mapa
        self.hraci = self.mapa.hraci

    def vymen_kartu(self, k2, k1, jm, jmT):
        """
        :return: vrátím index nakaženého hráče
        """
        hrac1 = self.hraci[jm]
        hrac2 = self.hraci[jmT]
        hrac1.spravuj_predmet(k1, -1)
        hrac1.spravuj_predmet(k2, 1)
        hrac2.spravuj_predmet(k1, 1)
        hrac2.spravuj_predmet(k2, -1)
        if k1 in ("Blood{0:d}".format(jm), "Infection") and k2!= "Gas":
            self.mapa.nakazeni[jmT] = True
            return jmT
        if k2 in ("Blood{0:d}".format(jmT), "Infection") and k1!= "Gas":
            self.mapa.nakazeni[jm] = True
            return jm

    # DRUHY ÚTOKÚ
    def strelba(self, jm, jmT, clovekT, pohyb = False):
        """
        :param jm: int(index střílejícího hráče)
        :param cil: tuple(int(parazit=None | klon=0 | clovek=1), int(index cíle))
        :param pohyb: tuple(pohyb) -- pokud střílí do sousední místnosti
        :return: int(míra poškození)
        """
        if not self.hraci[jm].naboje: return   #Musí mít náboje
        pozice = self.hraci[jm].pos[0][:]  #Střílí na cíl, který je s ním v místnosti
        if pohyb and pohyb != [0, 0]:
            if not self.hraci[jm].vylozeno[3]: return    #Musí mít puškohled, pokud chce střílet do vedlejší místnosti
            if self.mapa.kolize(jm, 0, pohyb): return
            pozice[0] += pohyb[0]
            pozice[1] += pohyb[1]
        zraneni = 1
        if clovekT is not None:  #Střílí na hráče
            if self.hraci[jmT].pos[clovekT] != pozice: return
            if self.hraci[jm].vylozeno[2] and (0 < self.hraci[jm].naboje) and self.hraci[jmT].zivoty[clovekT]:
                self.hraci[jm].odeber_naboje()
                #print("Střílím dvakrát")
                zraneni = 2
        else:   #Střílí na parazita
            dead = self.mapa.zranit_parazita(pozice, jmT)
            if dead is None: return     # Na té pozici žádný parazit nebyl
            if self.hraci[jm].vylozeno[3] and (1< self.hraci[jm].naboje) and not dead:
                self.hraci[jm].odeber_naboje()
                self.mapa.zranit_parazita(pozice, 1)
                zraneni = 2
        self.hraci[jm].odeber_naboje()
        return zraneni

    def bodnuti(self, jm, jmT, clovekT):
        """
        :param jm: int(index útočníka)
        :param cil: tuple(int(parazit=None|klon=0|clovek=1), int(index cíle))
        :return: False(pokud se bodnutí nepovedlo) | True
        """
        #print(self.hraci[jm].vylozeno[0])
        if not (self.hraci[jm].vylozeno[0]): return     # Je vyložený nůž?
        if randint(1, 4) < 2: return False   #Ten lamák se netrefil
        pozice = self.hraci[jm].pos[1]
        if clovekT is not None:
            if self.hraci[jmT].pos[clovekT] != pozice: return
            self.hraci[jmT].zranit(1, clovekT)
        else:
            if self.mapa.zranit_parazita(pozice, jmT) is None: return
        return True

    def granat(self, jm, clovek, pohyb):
        """
        :param jm: int (index hráče)
        :param clovek: int(klon|clovek)
        :param pohyb: tuple(smer hodu)
        :return: tuple(zasahnuti hraci [jm, clovek, zemrel], zasahnuti paraziti [index, zemrel])
        """
        if not self.hraci[jm].ma_predmet("Grenade"): return
        pozice = self.hraci[jm].pos[clovek][:]
        if pohyb != [0, 0]:
            pozice[0] += pohyb[0]
            pozice[1] += pohyb[1]
            if self.mapa.kolize(jm, clovek, pohyb): return
        for i, hrac in enumerate(self.hraci):
            if hrac.pos[0] == pozice:
                i, 0, hrac.zranit(1, 0)
            if hrac.pos[1] == pozice:
                hrac.zranit(1, 1)
        paraziti = []
        for p in self.mapa.paraziti:
            if p[0] == pozice:
                if p[2] == 2: paraziti.append([p[0], p[1], 1])
            else:
                paraziti.append(p)
        self.mapa.paraziti = paraziti

        self.hraci[jm].spravuj_predmet("Grenade", -1)
        return True

    def scan(self, jm, clovek, jmT, clovekT):
        """
        :param jm: int(index)
        :param cil: int(index cile) //Nezáleží jestli scanuju klona nebo člověka
        :return: list(predmety)
        """
        hrac = self.hraci[jm]
        if not hrac.spravuj_predmet("Scanner", -1): return
        if not (hrac.pos[clovek] == self.hraci[jmT].pos[clovekT]): return   # Musí být spolu v místnosti
        return (self.hraci[jmT].seznamKrve(), self.hraci[jmT].seznamPredmetu())

    def plosny_scan(self, jm, clovek):
        """
        :param jm: index hráče
        :param ind: clovek|klon
        :return: tuple(událost , počet nakažených mezi hráči)
        """
        y, x = self.hraci[jm].pos[clovek]
        if self.mapa.mapakaret[y][x][0] not in ("Terminal", "Terminal2"): return
        return (self.mapa.pouzij_mistnost(y, x), self.mapa.nakazeni.count(True))

    def otevri_dvere(self, jm ,ind):
        """
        :param jm: index hráče
        :param ind: clovek|klon
        :return: True
        """
        y, x = self.hraci[jm].pos[ind]
        if self.mapa.mapakaret[y][x][0] not in ("Terminal", "PCtwo"): return
        self.mapa.otevrenedvere = jm
        return self.mapa.pouzij_mistnost(y, x)

    def vypal_hnizdo(self, jm):
        y, x =self.hraci[jm].pos[1]
        if self.mapa.mapakaret[y][x][0] == "Nest" and self.hraci[jm].ma_predmet("Gas", 3): return True



class Hrac:
    def __init__(self, jmeno, avatar):
        self.pos = [[-1, -1],[-1, -1]]  #0= Klon, 1 = Clovek
        self.zivoty = [4, 4] #0= Klon, 1 = Clovek
        self.predmety = {k: 0 for k in Items.CARDS}
        self.vylozeno = [False, False, False, False]        #Knife | Card | Riffle | Scope
        self.jmeno = jmeno
        self.naboje = 0
        self.avatar= avatar
        self.krve = [avatar, avatar, avatar]

    def nazivu(self):
        return (self.zivoty[0] > 0) or (self.zivoty[1] > 0)

    def tahy(self):
        return int((self.zivoty[0] + 1) / 2) + int((self.zivoty[1] + 1) / 2)

    def zranit(self, poskozeni, figurka):
        self.zivoty[figurka] -= poskozeni
        if self.zivoty[figurka] <1:
            self.pos[figurka] = [-1, -1]
            return True
        return False

    def ma_predmet(self, predmet, pocet = 1):
        if predmet[:-1] == "Blood":
            if int(predmet[-1]) in self.krve: return True
        else:
            if self.predmety[predmet] >= pocet: return True
        return False

    def spravuj_predmet(self, predmet, x):
        #Přidat nebo odebrat předmět
        if predmet[:-1] == "Blood":
            if x == -1:
                try: self.krve.remove(int(predmet[-1]))
                except: return
            else:
                self.krve.append(int(predmet[-1]))
        else:
            if x < 0 and not self.ma_predmet(predmet): return
            self.predmety[predmet] += x
        #print("DOSTAL: ",self.avatar,"    ", predmet, x, "\n")
        return True

    def spawn(self):
        if self.pos[0] != [-1, -1]: return      #Pokud už je na mapě
        self.pos[0] = [int(Mapa.Y/2), int(Mapa.X/2)]
        self.pos[1] = [int(Mapa.Y/2), int(Mapa.X/2)]
        return True

    def odeber_naboje(self, x = 1):
        self.naboje -= x

    def vylecit(self, n1, n2):
        if (not self.zivoty[0] and n1) or (not self.zivoty[1] and n2): return   #Nebudu přidávat životy mrtvolám
        if not self.predmety["FirstAid"]: return
        if (self.zivoty[0] + n1) > 4 or (self.zivoty[1] + n2) > 4: return   #Hráč nemůže mít více jak 4 HP
        self.predmety["FirstAid"] -=1
        self.zivoty[0] +=n1
        self.zivoty[1] +=n2
        return True


    def vyloz_predmet(self, predmet):
        if not self.spravuj_predmet(predmet, -1): return
        if predmet == "Knife": self.vylozeno[0] = True
        elif predmet == "Card": self.vylozeno[1] = True
        elif predmet == "Riffle": self.vylozeno[2]= True
        elif predmet == "Scope": self.vylozeno[3] = True
        elif predmet == "Ammo": self.naboje += 4
        return True

    def seznamPredmetu(self):
        cards= []
        for key, value in self.predmety.items():
            if value: cards.append([key, value])
        return cards

    def seznamKrve(self):
        return ["Blood{0:d}".format(i) for i in self.krve]

    def karty(self):
        karty= 0
        for k,v in self.predmety.items():
            karty+= v
        karty += len(self.krve)
        return karty

    def me(self):
        me= (
            self.pos,
            self.zivoty,
            self.karty(),
            self.vylozeno,
            self.jmeno,
            self.naboje,
            self.avatar
        )
        return me

