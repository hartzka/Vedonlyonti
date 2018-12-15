from flask import render_template, request, redirect, url_for

from application import app, db, login_manager
from application.models import Base
from application.laji.models import Laji
from datetime import datetime, timedelta
from sqlalchemy.sql import text
from application.tapahtumajoukkue.models import Tapahtumajoukkue
from random import random, shuffle
import random
from application.veto.models import Veto
from application.auth.models import User
from flask_login import current_user
from application.tapahtumaveto.models import Tapahtumaveto
from application.tilitapahtuma.models import Tilitapahtuma
from application.joukkue.models import Joukkue


def arvoUusiTapahtuma(oldId, live):
        joukkueet = Joukkue.haeVapaatJoukkueet()
        result = []
        if (len(joukkueet) == 0):
            result.append({"old":-1}) #ei vapaita joukkueita
            return result
        shuffle(joukkueet)
        stmt = text("SELECT max(id) FROM tapahtuma")
        res = db.engine.execute(stmt)
        uusi_id = 0
        for row in res:
            if type(row[0]) == int:
                uusi_id = row[0]
        uusi_id = uusi_id+1    
        
        
        home_motivation = 1
        koti = 1

        home_attack = joukkueet[0]["attack"]
        home_defence = joukkueet[0]["defence"]
        home_tactic = joukkueet[0]["tactic"]

        j=1
        while(joukkueet[j]["laji_id"]!=joukkueet[0]["laji_id"]):
            j=j+1
        away_attack = joukkueet[j]["attack"]
        away_defence = joukkueet[j]["defence"]
        away_tactic = joukkueet[j]["tactic"]
                
        home_motivation = int(random.gauss(0, 7)) + int(random.gauss(3, 3))    
        away_motivation = int(random.gauss(0, 7))

        home_attack+=home_motivation
        home_defence+=home_motivation
        away_attack+=away_motivation
        away_defence+=away_motivation
        away_wins = 1 #avoid division by zero
        home_wins = 1
        draws = 1

        s = 0 #keskiarvoon lisättävä
        t = 0 #hajontaan lisättävä
        if (joukkueet[0]["laji_id"]==1): #jalkapallo
            s=-1
            t=-1
        elif (joukkueet[0]["laji_id"]==3): #koripallo
            s=75
            t=13
        for i in range(1000):
            home_goals = -1
            while (home_goals < 0):
                home_goals = int(random.gauss(2+s+(home_attack-away_defence)/10, 3+t)) + int(random.gauss(home_tactic/100, 1))

            away_goals = -1
            while (away_goals < 0):
                away_goals = int(random.gauss(2+s+(away_attack-home_defence)/10, 3+t)) + int(random.gauss(away_tactic/100, 1))

            if (home_goals > away_goals):
                home_wins = home_wins+1
            elif (home_goals < away_goals):
                away_wins = away_wins+1
            else:
                draws = draws+1

        kerroin1 = max(float("%.2f" % (980/home_wins + random.random()*0.4 - 0.2)),1.01)
        kerroinX = max(float("%.2f" % (980/draws + random.random()*0.4 - 0.2)),1.01)
        kerroin2 = max(float("%.2f" % (980/away_wins + random.random()*0.4 - 0.2)),1.01)  

        home_attack-=home_motivation
        home_defence-=home_motivation
        away_attack-=away_motivation
        away_defence-=away_motivation           
        
        a = random.randint(1,6)
        if (a==1):
            home_attack += home_motivation
        elif (a==2):
            home_defence += home_motivation
        elif (a==3):
            home_tactic += home_motivation
        elif (a==4):
            home_tactic += home_motivation
            home_attack += home_motivation
        elif (a==5):
            home_defence += home_motivation
            home_attack += home_motivation
        elif (a==6):
            home_tactic += home_motivation
            home_defence += home_motivation

        a = random.randint(1,6)
        if (a==1):
            away_attack += away_motivation
        elif (a==2):
            away_defence += away_motivation
        elif (a==3):
            away_tactic += away_motivation
        elif (a==4):
            away_tactic += away_motivation
            away_attack += away_motivation
        elif (a==5):
            away_defence += away_motivation
            away_attack += away_motivation
        elif (a==6):
            away_tactic += away_motivation
            away_defence += away_motivation
        if (live==True):
            se = 10    
        else:
            se=random.randint(60,300) #livetapahtuma ratkeaa heti
        t = Tapahtuma(joukkueet[0]["nimi"], joukkueet[j]["nimi"],
        joukkueet[0]["laji_id"], kerroin1, kerroinX, kerroin2, datetime.now()+timedelta(seconds=se),
        True, live)
        t.id = uusi_id
        
        tj1 = Tapahtumajoukkue(True, home_attack, home_defence, home_tactic, joukkueet[0]["id"], t.id)
        tj2 = Tapahtumajoukkue(False, away_attack, away_defence, away_tactic, joukkueet[j]["id"], t.id)
        laji = Laji.haeLaji(joukkueet[0]["laji_id"])
        
        result.append({"koti":joukkueet[0]["nimi"], "vieras":joukkueet[j]["nimi"], "laji":joukkueet[0]["laji_id"], "kerroin1":kerroin1, "kerroin2":kerroin2, "kerroinX":kerroinX, "date_expire":t.date_expire, "tj1":tj1, "tj2":tj2, "old":oldId, "id":t.id, "live":t.live})
    
        return result 


class Tapahtuma(Base):
    
    koti = db.Column(db.String, nullable=False)
    vieras = db.Column(db.String, nullable=False)
    kerroin1 = db.Column(db.DECIMAL, nullable=False)
    kerroinx = db.Column(db.DECIMAL, nullable=False)
    kerroin2 = db.Column(db.DECIMAL, nullable=False)
    laji_id = db.Column(db.Integer, db.ForeignKey('laji.id'),
                           nullable=False)
    date_expire = db.Column(db.DateTime)
    active = db.Column(db.Boolean, nullable= False)
    tulos = db.Column(db.String, nullable=False)
    live = db.Column(db.Boolean, nullable= False)

    def __init__(self, koti, vieras, laji, kerroin1, kerroinx, kerroin2, date_expire, active, live):
        
        self.laji_id = laji
        self.koti = koti
        self.vieras = vieras
        self.kerroin1 = kerroin1
        self.kerroin2 = kerroin2
        self.kerroinx = kerroinx
        self.date_expire = date_expire
        self.active=active
        self.tulos = "kesken"
        self.live = live

    @staticmethod
    def haeTulosvetokerroin(tapahtuma_id, veikkaus):

        home_motivation = 1
        koti = 1
        home_attack = 0
        away_attack = 0
        home_defence = 0
        away_defence = 0
        home_tactic = 0
        away_tactic = 0
        laji_id = 1

        stmt = text("SELECT attack, defence, tactic, tapahtumajoukkue.koti, laji_id FROM tapahtumajoukkue, tapahtuma"
                    " WHERE tapahtuma_id = :id"
                    " AND tapahtuma.id = :id2"
                    ).params(id=tapahtuma_id, id2=tapahtuma_id)
        res = db.engine.execute(stmt)
        for row in res:
            laji_id=row[4]
            if(row[3]==1):
                home_attack = row[0]
                home_tactic = row[2]
                home_defence = row[1]
            else:
                away_defence = row[1]
                away_attack = row[0]
                away_tactic = row[2]
                
        home_motivation = int(random.gauss(0, 7)) + int(random.gauss(3, 3))    
        away_motivation = int(random.gauss(0, 7))

        home_attack+=home_motivation
        home_defence+=home_motivation
        away_attack+=away_motivation
        away_defence+=away_motivation
        veikkaus_count = 1
        s = 0 #keskiarvoon lisättävä
        t = 0 #hajontaan lisättävä
        if (laji_id==1): #jalkapallo
            s=-1
            t=-1
        elif (laji_id==3): #koripallo
            s=75    
            t=13
        for i in range(50000):
            home_goals = -1
            while (home_goals < 0):
                home_goals = int(random.gauss(2+s+(home_attack-away_defence)/10, 3+t))+ int(random.gauss(home_tactic/100, 1))

            away_goals = -1
            while (away_goals < 0):
                away_goals = int(random.gauss(2+s+(away_attack-home_defence)/10, 3+t)) + int(random.gauss(away_tactic/100, 1))

            if (home_goals >= 10):
                home_goals = "10+"
            if (away_goals >= 10):
                away_goals = "10+"
            tulos = str(home_goals) + "-" + str(away_goals)
            if (tulos == veikkaus):
                veikkaus_count = veikkaus_count+1

        kerroin = max(float("%.2f" % (98000/veikkaus_count + random.random()*0.4 - 0.2)),1.01)
        return kerroin
        

    @staticmethod
    def haeMonivetoTapahtuma(live):
        
        #palauttaa listan monivetotapahtumista (3) with koti, vieras, laji, kerroin, date_expire
        #laittaa expiredeiksi tapahtumat, jotka menneet umpeen
        good_events = 0
        present = datetime.now()

        stmt = text("SELECT tapahtuma.id, date_expire, live"
                    " FROM tapahtuma, laji"
                    " WHERE active = True"
                    " AND laji.id = tapahtuma.laji_id"
                    " AND live = :live"
                     ).params(live=live)
        res = db.engine.execute(stmt)

        response = []
        
        for row in res:
            d = datetime.strptime(str(row[1]), '%Y-%m-%d %H:%M:%S.%f')
            
        
            if(d < present):
                
                t = arvoUusiTapahtuma(row[0], live) #palautaa taulukon, jossa koti, vieras, laji, kerroin, date_expire

                response.append(t)
                return response
     
            else:
                good_events = good_events+1
                if (good_events >= 6):
                    return response
                
        while (len(response) < 1):
            t = arvoUusiTapahtuma(0, live)
     
            response.append(t)
            
        return response


    @staticmethod
    def haeMonivetoTapahtumat(live):
        
        #palauttaa listan monivetotapahtumista (3) with koti, vieras, laji, kerroin, date_expire, live
        
        present = datetime.now()
        stmt = text("SELECT tapahtuma.id, koti, vieras, laji_id, kerroin1, kerroin2, kerroinx, date_expire, live"
                    " FROM tapahtuma, laji"
                    " WHERE active = True"
                    " AND laji.id = tapahtuma.laji_id"
                    " AND live = :live"
                     ).params(live=live)
        res = db.engine.execute(stmt)

        response = []
        
        for row in res:
            d = str(datetime.strptime(str(row[7]), '%Y-%m-%d %H:%M:%S.%f'))
            d = d[0:16]
            response.append({"id":row[0], "koti":row[1], "vieras":row[2], "laji":Laji.haeLaji(row[3]), "kerroin1":row[4], "kerroin2":row[5], "kerroinX":row[6], "date_expire":d})
                
        return response

    @staticmethod
    def haeTulosvetoTapahtumat():
        
        present = datetime.now()
        #ei koripalloa tulosvetoon!
        stmt = text("SELECT tapahtuma.id, koti, vieras, laji_id, kerroin1, kerroin2, kerroinx, date_expire"
                    " FROM tapahtuma, laji"
                    " WHERE active = True"
                    " AND laji.id = tapahtuma.laji_id"
                    " AND laji.id NOT IN (3)"
                     )
        res = db.engine.execute(stmt)

        response = []
        
        for row in res:
            d = str(datetime.strptime(str(row[7]), '%Y-%m-%d %H:%M:%S.%f'))
            d = d[0:16]
            response.append({"id":row[0], "koti":row[1], "vieras":row[2], "laji":Laji.haeLaji(row[3]), "kerroin1":row[4], "kerroin2":row[5], "kerroinX":row[6], "date_expire":d})
        
        while(len(response) < 6):
            response.append({})
        return response
    
    @staticmethod
    def haeTulosvetoTapahtumat_groupByLaji():
        
        present = datetime.now()
        #ei koripalloa tulosvetoon!
        stmt = text("SELECT tapahtuma.id, koti, vieras, laji_id, kerroin1, kerroin2, kerroinx, date_expire"
                    " FROM tapahtuma, laji"
                    " WHERE active = True"
                    " AND laji.id = tapahtuma.laji_id"
                    " AND laji.id NOT IN (3)"
                    " GROUP BY date_expire, tapahtuma.id, laji.id ORDER BY laji.id"
                     )
        res = db.engine.execute(stmt)

        response = []
        
        for row in res:
            d = str(datetime.strptime(str(row[7]), '%Y-%m-%d %H:%M:%S.%f'))
            d = d[0:16]
            response.append({"id":row[0], "koti":row[1], "vieras":row[2], "laji":Laji.haeLaji(row[3]), "kerroin1":row[4], "kerroin2":row[5], "kerroinX":row[6], "date_expire":d})
        
        while(len(response) < 6):
            response.append({})
        return response
    

    @staticmethod
    def haeMonivetoTapahtumat_groupByLaji(live):
        
        #palauttaa listan monivetotapahtumista (3) with koti, vieras, laji, kerroin, date_expire, live
        
        present = datetime.now()

        stmt = text("SELECT tapahtuma.id, koti, vieras, laji_id, kerroin1, kerroin2, kerroinx, date_expire, live"
                    " FROM tapahtuma, laji"
                    " WHERE active = True"
                    " AND laji.id = tapahtuma.laji_id"
                    " AND live = :live"
                    " GROUP BY date_expire,tapahtuma.id,laji.id ORDER BY laji.id"
                     ).params(live=live)
        res = db.engine.execute(stmt)

        response = []
        
        for row in res:
            d = str(datetime.strptime(str(row[7]), '%Y-%m-%d %H:%M:%S.%f'))
            d = d[0:16]
            response.append({"id":row[0], "koti":row[1], "vieras":row[2], "laji":Laji.haeLaji(row[3]), "kerroin1":row[4], "kerroin2":row[5], "kerroinX":row[6], "date_expire":d})
                
        return response
    
    @staticmethod
    def haeTulosvetoTapahtumaById(tapahtuma_id):
        
        #palauttaa listan monivetotapahtumista (3) with koti, vieras, laji, kerroin, date_expire
        #laittaa expiredeiksi tapahtumat, jotka menneet umpeen
        good_events = 0
        present = datetime.now()

        stmt = text("SELECT tapahtuma.id, koti, vieras, laji_id, kerroin1, kerroin2, kerroinx, date_expire"
                    " FROM tapahtuma, laji"
                    " WHERE active = True"
                    " AND laji.id = tapahtuma.laji_id"
                    " AND tapahtuma.id = :id"
                     ).params(id=tapahtuma_id)
        res = db.engine.execute(stmt)

        response = []
        
        for row in res:
            d = str(datetime.strptime(str(row[7]), '%Y-%m-%d %H:%M:%S.%f'))
            d = d[0:16]
            response.append({"id":row[0], "koti":row[1], "vieras":row[2], "laji":Laji.haeLaji(row[3]), "kerroin1":row[4], "kerroin2":row[5], "kerroinX":row[6], "date_expire":d})
                
                
        return response

    @staticmethod
    def haeMonivetoTapahtumatByVetoId(veto_id):
        
        #palauttaa listan monivetotapahtumista (3) with koti, vieras, laji, kerroin, date_expire
        #laittaa expiredeiksi tapahtumat, jotka menneet umpeen
        good_events = 0
        present = datetime.now()

        stmt = text("SELECT veikkaus, tapahtuma_id, id"
                    " FROM tapahtumaveto"
                    " WHERE veto_id = :id"
                    ).params(id=veto_id)
        res = db.engine.execute(stmt)
        response = []

        for row in res:
            stmt2 = text("SELECT tapahtuma.id, koti, vieras, laji_id, kerroin1, kerroin2, kerroinx"
                    " FROM tapahtuma, laji"
                    " WHERE tapahtuma.id = :id"
                    " AND laji.id = tapahtuma.laji_id"
                     ).params(id=row[1])
            res2 = db.engine.execute(stmt2)

            for row2 in res2:
                response.append({"tapahtumaveto_id":row[2], "tapahtuma_id":row2[0], "koti":row2[1], "vieras":row2[2], "laji":Laji.haeLaji(row2[3]), "kerroin1":row2[4], "kerroin2":row2[5], "kerroinX":row2[6], "veikkaus":row[0]})

        while(len(response)<6):
            response.append({"veikkaus":"-", "tapahtumaveto_id":0})        
        return response
    
    @staticmethod
    def haeTulos(tapahtuma_id):
        stmt = text("SELECT tulos FROM tapahtuma"
                     " WHERE tapahtuma.id = :id"
                     ).params(id=tapahtuma_id)
        res = db.engine.execute(stmt)

        response = ""
        for row in res:
            response = row[0]
            
        return response

    @staticmethod
    def isActive(tapahtuma_id):
        stmt = text("SELECT active FROM tapahtuma"
                     " WHERE tapahtuma.id = :id"
                     ).params(id=tapahtuma_id)
        res = db.engine.execute(stmt)

        response = ""
        for row in res:
            response = row[0]
            
        return response
    
    @staticmethod
    def do_veto_routines(live):
        present = datetime.now()

        poistettavat = Veto.haePoistettavat() #poistettavat tapahtumat, jotka ei liity vetoihin
        for tid in poistettavat:
            stmt = text("DELETE FROM tapahtuma WHERE id = :id"
            ).params(id = tid)
            db.engine.execute(stmt)

    #tulosten päivitys valmiille tapahtumille
        stmt = text("SELECT id, date_expire, laji_id FROM tapahtuma WHERE active = True")
        res = db.engine.execute(stmt)
        tapahtumajoukkueet = []
        tapahtumat = []
        for row in res:
            time = datetime.strptime(str(row[1]), '%Y-%m-%d %H:%M:%S.%f')
            if (time < present):
                stmt2 = text("SELECT id, koti, attack, defence, tactic FROM tapahtumajoukkue WHERE tapahtuma_id = :id"
                ).params(id=row[0])
                res2 = db.engine.execute(stmt2)
                response = []
                for row2 in res2:
                    tapahtumajoukkue_id = row2[0] 
                    koti = row2[1]
                    attack = row2[2]
                    defence = row2[3]
                    tactic = row2[4]
                
                    response.append({"id": tapahtumajoukkue_id, "koti":koti, "attack":attack, "defence":defence, "tactic":tactic})

                home_goals = -1
                s = 0 #keskiarvoon lisättävä
                t = 0 #hajontaan lisättävä
                if (row[2]==1): #jalkapallo
                    s=-1
                    t=-1
                elif (row[2]==3): #koripallo
                    s=75
                    t=13
                while (home_goals < 0):
                    home_goals = int(random.gauss(2+s+(response[0]["attack"]-response[1]["defence"])/10, 3+t)) + int(random.gauss(response[0]["tactic"]/100, 1))

                away_goals = -1
                while (away_goals < 0):
                    away_goals = int(random.gauss(2+s+(response[1]["attack"]-response[0]["defence"])/10, 3+t)) + int(random.gauss(response[1]["tactic"]/100, 1))

                koti = 0
                if (response[0]["koti"] == 1):
                    koti = 1
            
                koti_id = response[koti]["id"]
                vieras_id = response[1-koti]["id"]

                tulos = ""
                tulos = tulos + str(home_goals) + "-" + str(away_goals)

                tapahtumajoukkueet.append({"goals":home_goals, "id":koti_id})
                tapahtumajoukkueet.append({"goals":away_goals, "id":vieras_id})
                tapahtumat.append({"tulos":tulos, "id":row[0]})


        for tapahtuma in tapahtumat:
            stm = text("UPDATE tapahtuma SET tulos = :tulos WHERE id = :id"
            ).params(tulos=tapahtuma["tulos"], id=tapahtuma["id"])
            db.engine.execute(stm)
            

        for tj in tapahtumajoukkueet:
            stm = text("UPDATE tapahtumajoukkue SET pisteet = :goals WHERE id = :id"
            ).params(goals=tj["goals"], id=tj["id"])
            db.engine.execute(stm)

    #tarkistus ratkenneille vedoille, onko oikein
        vedot = User.haeVedot(current_user.id)
        for veto in vedot:
            oikein = True
            active = False
            tapahtumavedot = Tapahtumaveto.haeVedot(veto["id"])
         
            if (len(tapahtumavedot) == 0):
                oikein = False
            for tapahtumaveto in tapahtumavedot:
                if(Tapahtuma.isActive(tapahtumaveto["tapahtuma_id"])):
                    active=True
          
                tulos = Tapahtuma.haeTulos(tapahtumaveto["tapahtuma_id"])
          
                if (tulos == "kesken" or tulos == ""):
                    oikein = False
                    break
                
                koti = ""
                vieras = ""
                i=0
                while(tulos[i]!="-"):
                    koti=koti+tulos[i]
                    i=i+1
                vieras=int(tulos[i+1:])
                koti=int(koti)
                
                veikkaus = tapahtumaveto["veikkaus"]
                
                if(tapahtumaveto["name"] == "moniveto"):
                    
                    if (koti > vieras and veikkaus != "1"):
                        oikein = False
                        break
                    elif (koti < vieras and veikkaus != "2"):
                        oikein = False
                        break    
                    elif (koti == vieras and veikkaus != "X"):
                        oikein = False
                        break  
                elif(tapahtumaveto["name"] == "tulosveto"):
            
                    veikkaus_koti = "" #veikkauskoti
                    veikkaus_vieras = "" #veikkausvieras
                    i=0
                    while(veikkaus[i]!="-"):
                        veikkaus_koti=veikkaus_koti+veikkaus[i]
                        i=i+1
                    veikkaus_vieras=(veikkaus[i+1:])
                    if(veikkaus_vieras[len(veikkaus_vieras)-1] == "+"):
                        veikkaus_vieras=veikkaus_vieras[0:len(veikkaus_vieras)-1]
                    if(veikkaus_koti[len(veikkaus_koti)-1] == "+"):
                        veikkaus_koti=veikkaus_koti[0:len(veikkaus_koti)-1]
                    veikkaus_koti=int(veikkaus_koti)
                    veikkaus_vieras=int(veikkaus_vieras)
                    
                    if(koti >= 10 and veikkaus_koti == 10 and vieras==veikkaus_vieras):
                        break
                    elif(vieras >= 10 and veikkaus_vieras == 10 and koti==veikkaus_koti):
                        break
                    elif(koti >= 10 and veikkaus_koti == 10 and vieras >= 10 and veikkaus_vieras == 10):
                        break
                    elif (koti != veikkaus_koti):
                        oikein = False
                        break
                    elif (vieras != veikkaus_vieras):
                        oikein = False
                        break
                  
            if ((oikein == True) and (active == True)):
            #pelivoittojen käsittely
                kerroin = float("%.2f" % float(veto["kerroin"]))
                panos = int(veto["panos"])
                voitto = kerroin*panos
                voitto = ("%.2f" % voitto)
            
                t = Tilitapahtuma("Pelivoitto", voitto)
                t.account_id = current_user.id
                rahat = current_user.getRahat()

                rahat = float(rahat) + float(voitto)
                current_user.rahat = rahat

                stm = text("UPDATE veto SET voitto = :voitto WHERE id = :id"
                ).params(voitto=voitto, id=veto["id"])
                db.engine.execute(stm)
                db.session().add(t)
                db.session().commit()

        present = datetime.now()

        for tapahtuma in tapahtumat:
            stm2 = text("UPDATE tapahtuma SET active = False WHERE id = :id"
            ).params(id=tapahtuma["id"])
            db.engine.execute(stm2)
    
        for i in range (6):
            #uusien tapahtumien luonti
            tapahtumat = Tapahtuma.haeMonivetoTapahtuma(live)
            if (len(tapahtumat) == 0):
                break
            #turhien tapahtumajoukkueiden poisto
            if (tapahtumat[0][0]["old"] == -1):
                stmt2 = text("DELETE FROM tapahtumajoukkue WHERE tapahtuma_id NOT IN"
                " (SELECT id FROM tapahtuma WHERE active = True)"
                )
                db.engine.execute(stmt2)
                tapahtumat = Tapahtuma.haeMonivetoTapahtuma(live)
       
            row = tapahtumat[0][0]
            tj1 = row["tj1"]
            tj2 = row["tj2"]
            t = Tapahtuma(row["koti"], row["vieras"],
            row["laji"], row["kerroin1"], row["kerroinX"], row["kerroin2"],
            row["date_expire"], True, row["live"])
            t.id = row["id"]
            db.session().add(t)
            db.session().commit()
            db.session().add(tj1)
            db.session().add(tj2)
            db.session().commit()
            stmt = text("UPDATE tapahtuma SET active = False WHERE id = :id"
                     ).params(id=row["old"])
            db.engine.execute(stmt)


