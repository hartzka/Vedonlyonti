from flask import render_template, request, redirect, url_for

from application import app, db, login_manager
from application.models import Base
from application.laji.models import Laji
from datetime import datetime, timedelta
from sqlalchemy.sql import text
from application.tapahtumajoukkue.models import Tapahtumajoukkue
from random import random, shuffle
import random

def haeVapaatJoukkueet():
        stmt = text("SELECT id, nimi, attack, defence, tactic, laji_id"
                    " FROM joukkue"
                     " WHERE id NOT IN (SELECT tapahtumajoukkue.joukkue_id"
                     " FROM tapahtumajoukkue)"
                     )
        res = db.engine.execute(stmt)
        response = []
        
        for row in res:
            response.append({"id":row[0], "nimi":row[1], "attack":row[2], "defence":row[3], "tactic":row[4], "laji_id":row[5]})
        return response



def arvoUusiTapahtuma(oldId):
        joukkueet = haeVapaatJoukkueet()
        result = []
        if (len(joukkueet) == 0):
            result.append({"old":-7})
            return result
        shuffle(joukkueet)
        stmt = text("SELECT max(id) FROM tapahtuma")
        res = db.engine.execute(stmt)
        uid = 0
        for row in res:
            if type(row[0]) == int:
                uid = row[0]
        uid = uid+1    
        
        
        home_motivation = 1
        koti = 1

        home_attack = joukkueet[0]["attack"]
        away_attack = joukkueet[1]["attack"]
        home_defence = joukkueet[0]["defence"]
        away_defence = joukkueet[1]["defence"]
        home_tactic = joukkueet[0]["tactic"]
        away_tactic = joukkueet[1]["tactic"]
                
        home_motivation = int(random.gauss(0, 7)) + int(random.gauss(3, 3))    
        away_motivation = int(random.gauss(0, 7))

        home_attack+=home_motivation
        home_defence+=home_motivation
        away_attack+=away_motivation
        away_defence+=away_motivation
        away_wins = 0
        home_wins = 0
        draws = 0

        for i in range(1000):
            home_goals = -1
            while (home_goals < 0):
                home_goals = int(random.gauss(2+(home_attack-away_defence)/10, 3)) + int(random.gauss(home_tactic/100, 1))

            away_goals = -1
            while (away_goals < 0):
                away_goals = int(random.gauss(2+(away_attack-home_defence)/10, 3)) + int(random.gauss(away_tactic/100, 1))

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
                
        t = Tapahtuma(joukkueet[0]["nimi"], joukkueet[1]["nimi"],
        joukkueet[0]["laji_id"], kerroin1, kerroinX, kerroin2, datetime.now()+timedelta(minutes=2),
        True)
        t.id = uid
        
        tj1 = Tapahtumajoukkue(True, home_attack, home_defence, home_tactic, joukkueet[0]["id"], t.id)
        tj2 = Tapahtumajoukkue(False, away_attack, away_defence, away_tactic, joukkueet[1]["id"], t.id)
        laji = haeLaji(joukkueet[0]["laji_id"])
        
        result.append({"koti":joukkueet[0]["nimi"], "vieras":joukkueet[1]["nimi"], "laji":joukkueet[0]["laji_id"], "kerroin1":kerroin1, "kerroin2":kerroin2, "kerroinX":kerroinX, "date_expire":t.date_expire, "tj1":tj1, "tj2":tj2, "old":oldId, "id":t.id})
    
        return result 

def haeLaji(laji_id=0):
        stmt = text("SELECT nimi"
                    " FROM laji"
                     " WHERE id = :id"
                     ).params(id = laji_id)
        res = db.engine.execute(stmt)
        response = []
        
        for row in res:
            response.append({"nimi":row[0]})

        return response[0]["nimi"]     



class Tapahtuma(Base):
    
    koti = db.Column(db.String, nullable=False)
    vieras = db.Column(db.String, nullable=False)
    kerroin1 = db.Column(db.DECIMAL, nullable=False)
    kerroinX = db.Column(db.DECIMAL, nullable=False)
    kerroin2 = db.Column(db.DECIMAL, nullable=False)
    laji_id = db.Column(db.Integer, db.ForeignKey('laji.id'),
                           nullable=False)
    date_expire = db.Column(db.DateTime)
    active = db.Column(db.Boolean, nullable= False)
    tulos = db.Column(db.String, nullable=False)
    


    def __init__(self, koti, vieras, laji, kerroin1, kerroinX, kerroin2, date_expire, active):
        
        self.laji_id = laji
        self.koti = koti
        self.vieras = vieras
        self.kerroin1 = kerroin1
        self.kerroin2 = kerroin2
        self.kerroinX = kerroinX
        self.date_expire = date_expire
        self.active=active
        self.tulos = "kesken"


    @staticmethod
    def haeMonivetoTapahtuma():
        
        #palauttaa listan monivetotapahtumista (3) with koti, vieras, laji, kerroin, date_expire
        #laittaa expiredeiksi tapahtumat, jotka menneet umpeen
        good_events = 0
        present = datetime.now()

        stmt = text("SELECT tapahtuma.id, date_expire"
                    " FROM tapahtuma, laji"
                    " WHERE active = 1"
                    " AND laji.id = tapahtuma.laji_id"
                     )
        res = db.engine.execute(stmt)

        response = []
        
        for row in res:
            d = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S.%f')
            
        
            if(d < present):
                
                t = arvoUusiTapahtuma(row[0]) #palautaa taulukon, jossa koti, vieras, laji, kerroin, date_expire

                response.append(t)
                return response
     
            else:
                good_events = good_events+1
                if (good_events >= 3):
                    return response
                
        while (len(response) < 1):
            t = arvoUusiTapahtuma(0)
     
            response.append(t)
            
        return response


    @staticmethod
    def haeMonivetoTapahtumat():
        
        #palauttaa listan monivetotapahtumista (3) with koti, vieras, laji, kerroin, date_expire
        #laittaa expiredeiksi tapahtumat, jotka menneet umpeen
        good_events = 0
        present = datetime.now()

        stmt = text("SELECT tapahtuma.id, koti, vieras, laji_id, kerroin1, kerroin2, kerroinX, date_expire"
                    " FROM tapahtuma, laji"
                    " WHERE active = 1"
                    " AND laji.id = tapahtuma.laji_id"
                     )
        res = db.engine.execute(stmt)

        response = []
        
        for row in res:
            d = str(datetime.strptime(row[7], '%Y-%m-%d %H:%M:%S.%f'))
            d = d[0:16]
            response.append({"id":row[0], "koti":row[1], "vieras":row[2], "laji":haeLaji(row[3]), "kerroin1":row[4], "kerroin2":row[5], "kerroinX":row[6], "date_expire":d})
                
                
        return response
    
    @staticmethod
    def haeTulos(tapahtuma_id):
        stmt = text("SELECT tulos FROM tapahtuma"
                     " WHERE active = 1 AND tapahtuma.id = :id"
                     ).params(id=tapahtuma_id)
        res = db.engine.execute(stmt)

        response = ""
        for row in res:
            response = row[0]
            
        return response
