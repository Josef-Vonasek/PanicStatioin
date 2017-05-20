
class Items:
    ROOMS= (["FirstAid", (2, 0, 0, 0), True, "room12"],     # Léčení
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

    CARDS= {"FirstAid": "FirstAid",
            "Scanner": "Scanner",
            "Ammo": "Ammo",
            "Grenade": "Grenade",
            "Scope": "Scope",
            "Riffle": "Riffle",
            "Vest": "Vest",
            "Gas": "Gas",
            "Infection": "Infection",
            "Card": "Card",
            "EnergyDrink": "EnergyDrink",
            "Knife": "Knife",
            "Parasite": "Parasite"
    }

    def __init__(self):
        pass


class Mapa:
    def __init__(self, pristimistnost, ppredmetu, mapa, parazitimax, paraziti, phraci):

        self.mapakaret = mapa
        if pristimistnost is None:
            self.pristimistnost = (None, None, None, "", None)
        else:
            self.pristimistnost= Items.ROOMS[pristimistnost][:]
        self.pocetpredmetu= ppredmetu
        self.parazitimax = parazitimax
        self.otevrenedvere = -1

        self.smery = ((0, 2), (1, 3))
        self.paraziti= paraziti

        self.hraci = []
        self.hrac = None

    def other_players(self):
        p = self.hraci
        p.remove(self.hrac)
        return p

    def nacti_hrace(self, ja, hraci):
        """
        :param ja: tuple(index, predmety, krve)
        :param hraci: list(udaje hracu)
        :return: None
        inicializuje všechny hráče - přiřadí předměty, životy, pozice atd.
        """
        self.ja = ja[0]
        for args in hraci:
            self.hraci.append(SpoluHrac(*args))

        self.hrac= Hrac(*hraci[ja[0]])
        self.hraci[ja[0]]= self.hrac

        #print (self.hraci, self.hrac)
        self.hrac.predmety= ja[1]
        self.hrac.krve = ja[2]
        self.hrac.nakazeny = ja[3]


    def pohyb_hrace(self, jm, clovek, pohyb):
        # Pohyb ve skutečnosti udává směr pohybu
        # Vrací: False = hráč se nemůže pohnout | None =  hráč se pohne, ale s nikým se nesetká | Tuple setkání
        self.hraci[jm].pos[clovek][0] += pohyb[0]
        self.hraci[jm].pos[clovek][1] += pohyb[1]
        y, x = self.hraci[jm].pos[clovek]
        if self.mapakaret[y][x][0] == "Reactor":
            return [[0, 0, 0]]
        return self.setkani(jm, clovek)


    def pohyb_parazitu(self, pohyb):
        """
        POHNE všemi parazity ve zvoleném směru, pokud je to možné
        :return:
        """
        y1, x1 = pohyb
        for i, p in enumerate(self.paraziti[:]):
            (y, x), count, type = p
            if not self.kolize(i, None, pohyb):
                self.paraziti[i][0][0] +=y1
                self.paraziti[i][0][1] +=x1

        #Kdyby bylo více parazitů se stejnými souřadnicemi v seznam parazitu, tak je dám k sobě dohromady
        paraziti= []
        for p in self.paraziti:
            for p1 in paraziti:
                if p1[0] == p[0] and p1[2] == p[2]:
                    p1[1] += p[1]
                    break
            else:
                paraziti.append(p)
        return paraziti

    def pritahni_parazita(self, index, souradnice):
        p = self.paraziti[index]
        self.odeber_parazita(index)
        self.pridej_parazita(souradnice, p[2])

    def vyvolej_parazita(self, parazit):
        self.pridej_parazita(*parazit)
        #print ("PRIDAVAM:", self.paraziti)

    def pridej_parazita(self, souradnice, type):
        for i in range(len(self.paraziti)):
            if souradnice == self.paraziti[i][0] and type == self.paraziti[i][2]:
                self.paraziti[i][1]+= 1
                return
        self.paraziti.append([souradnice, 1, type])

    def odeber_parazita(self, index):
        if self.paraziti[index][1] == 1:
            del self.paraziti[index]
        else:
            self.paraziti[index][1] -=1

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
        """
        :param pohyb: tuple(smer pohybu)
        :return: vrací index pod kterým hledat v mapě dveře tuple(místnost ve které stojím, sousedící místnost)
        """
        if pohyb[0]:
            if pohyb[0] == 1: return (2, 0)
            if pohyb[0] == -1: return (0, 2)
        if pohyb[1]:
            if pohyb[1] == 1: return (1, 3)
            if pohyb[1] == -1: return (3, 1)

    def sousedi(self, y, x, clovek):
        """
        :param y: ....
        :param x: ....
        :param clovek: int(člověk nebo klon?)
        :return: vrací smer pohybu, v kterém sousedí figurka s pozicí y, x
        """
        if y==self.hrac.pos[clovek][0]:
            if x== (self.hrac.pos[clovek][1]+ 1): return ( 0, 1)
            if x== (self.hrac.pos[clovek][1]- 1): return (0, -1)
        if x==self.hrac.pos[clovek][1]:
            if y== (self.hrac.pos[clovek][0]+ 1): return ( 1, 0)
            if y== (self.hrac.pos[clovek][0]- 1): return (-1, 0)


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
                if karta or self.otevrenedvere > -1: return False
                else: return True
        return True

    def prevrat_mistnost(self, m):
        return (m[2], m[3], m[0], m[1])

    def vrat_mistnost(self, index, prevratit):
        mistnost= Items.ROOMS[index][:]
        if prevratit:
            mistnost[1] = self.prevrat_mistnost(mistnost[1])
        return mistnost

    def objevit_mistnost(self, pos, mistnost, prevratit, pmistnost):
        y, x= pos
        if pmistnost is None:
            self.pristimistnost= (None, None, None, "", None)
        else:
            self.pristimistnost = Items.ROOMS[pmistnost][:]
        self.mapakaret[y][x] = self.vrat_mistnost(mistnost, prevratit)

    def _objevit_mistnost(self, clovek, y, x, obratit):
        """
        Vyzkouší, zdali je možné objevit místnost v souladu s pravidly, a poté vrátí potřebné argumenty pro zaslání příkazu serveru.
        Funkce musí zjistit jestli objevuje Klon NEBO ČLOVĚK, protože zná pouze y,x objevené místnosti
        """
        pohyb= self.sousedi(y, x, clovek)
        if not pohyb: return
        yf, xf = self.hrac.pos[clovek]

        mistnost= obratit and self.prevrat_mistnost(self.pristimistnost[1]) or self.pristimistnost[1]   #Převratím místnost, pokud je potřeba
        smer= self.vrat_smer(pohyb)
        # Pokud nebrání ve výhledu stěna A místnost není objevená A v tomto směru je průchod do místnosti
        if self.mapakaret[yf][xf][1][smer[0]] and not self.mapakaret[yf+pohyb[0]][xf+pohyb[1]] and mistnost[smer[1]]:
            return (clovek, pohyb, obratit)


    def setkani(self, jm, clovek, pohyb= (0, 0), paraziti= False):
        """
        Vrátí seznam setkání kde poslední prvek udává setkání parazitů
        [[bool(klon), bool(clovek), int(index)], ...., [int(parazit 0), int(p 1), int(p 2)]]
        """
        y, x = self.hraci[jm].pos[clovek]
        y+= pohyb[0]
        x+= pohyb[1]
        shracu= []
        sparazitu= [0, 0, 0]
        for i, h in enumerate(self.hraci):
            if i == jm: continue
            if [y, x] in h.pos:
                new = [False, False, i]
                if [y, x] == h.pos[0]: new[0] = True
                if [y, x] == h.pos[1]: new[1] = True
                shracu.append(new)

        if paraziti is False: return shracu + [[0, 0, 0]]

        for i, p in enumerate(self.paraziti):
            if [y, x] == p[0]: sparazitu[p[2]] += p[1]
        if shracu or sparazitu != [0, 0, 0]:
            return shracu + [sparazitu]
        return []

    def __str__(self):
        text = ""
        for i in self.mapakaret:
            text += "%s\n" %i
        return text

class Hrac:
    def __init__(self, pos, zivoty, karty, vylozeno, jmeno, naboje, avatar):
        self.pos = pos
        self.zivoty = zivoty
        self.karty= karty
        self.vylozeno = vylozeno
        self.jmeno = jmeno
        self.naboje = naboje
        self.avatar= avatar
        self.krve = []
        self.predmety = {}
        self.nakazeny = False

    def zranit(self, poskozeni, figurka):
        self.zivoty[figurka] -= poskozeni
        if self.zivoty[figurka] <1:
            self.pos[figurka][0] = -1
            self.pos[figurka][1] = -1
            return True
        return False

    def tahy(self):
        return int((self.zivoty[0] + 1)/2) + int((self.zivoty[1] + 1)/2)

    def ma_predmet(self, predmet):
        if predmet[:-1] == "Blood":
            if int(predmet[-1]) in self.krve: return True
        else:
            if self.predmety[predmet] > 0: return True
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
        return True

    def spawn(self):
        self.pos[0] = [int(25/2), int(27/2)]
        self.pos[1] = [int(25/2), int(27/2)]


    def odeber_naboje(self, x = 1):
        self.naboje -= x

    def vylecit(self, n1, n2):
        if (not self.zivoty[0] and n1) or (not self.zivoty[1] and n2): return   #Nebudu přidávat životy mrtvolám
        if not self.predmety["FirstAid"]: return
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

    def seznamPredmetu(self):
        cards= []
        for key, value in self.predmety.items():
            if value: cards.append([Items.CARDS[key], value])
        return cards

    def me(self):
        karty= 0
        for k,v in self.predmety.items():
            karty+= v
        karty += len(self.krve)
        return [self.pos, self.zivoty, self.avatar, self.vylozeno, self.jmeno, self.naboje, karty]

class SpoluHrac(Hrac):

    def ma_predmet(self, predmet):
        return

    def spravuj_predmet(self, predmet, x):
        self.karty += x

    def vylecit(self, n1, n2):
        self.karty -=1
        self.zivoty[0] +=n1
        self.zivoty[1] +=n2

    def vyloz_predmet(self, predmet):
        self.karty -=1
        if predmet == "Knife": self.vylozeno[0] = True
        elif predmet == "Card": self.vylozeno[1] = True
        elif predmet == "Riffle": self.vylozeno[2]= True
        elif predmet == "Scope": self.vylozeno[3] = True
        elif predmet == "Ammo": self.naboje += 4

    def seznamPredmetu(self):
        return

    def me(self):
        return [self.pos, self.zivoty, self.avatar, self.vylozeno, self.jmeno, self.naboje, self.karty]