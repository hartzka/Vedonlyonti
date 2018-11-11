from flask import render_template, request, redirect, url_for

from application import app, db, login_manager
from application.models import Base
from datetime import datetime, timedelta
from sqlalchemy.sql import text
from application.tapahtumajoukkue.models import Tapahtumajoukkue

def haeVapaatJoukkueet():
        stmt = text("SELECT id, nimi, attack, defence, tactic, laji_id"
                    " FROM joukkue"
                     " WHERE joukkue.id NOT IN (SELECT tapahtumajoukkue.joukkue_id"
                     " FROM tapahtumajoukkue)"
                     )
        res = db.engine.execute(stmt)
        response = []
        
        for row in res:
            response.append({"id":row[0], "nimi":row[1], "attack":row[2], "defence":row[3], "tactic":row[4], "laji_id":row[5]})

        print(response)
        print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        return response

def arvoUusiTapahtuma():
        joukkueet = haeVapaatJoukkueet()
        t = Tapahtuma(joukkueet[0]["nimi"], joukkueet[1]["nimi"],
        joukkueet[0]["laji_id"], 2,
        datetime.now()+timedelta(seconds = 180))
        print(t)
        print(joukkueet)
        print(joukkueet[0]["nimi"])
        db.session().add(t)
        db.session().commit()

        print("1111111111111111111111111111111111111111111111")

        motivation = 1
        koti = 1
        tj1 = Tapahtumajoukkue(True, joukkueet[0]["attack"]+motivation+koti, joukkueet[0]["defence"]+motivation+koti, joukkueet[0]["tactic"]+motivation+koti, joukkueet[0]["id"], t.id)
        tj2 = Tapahtumajoukkue(False, joukkueet[1]["attack"]+motivation, joukkueet[1]["defence"]+motivation, joukkueet[1]["tactic"]+motivation, joukkueet[1]["id"], t.id)
        laji = haeLaji(joukkueet[0]["laji_id"])
        db.session().add(tj1)
        db.session().add(tj2)
        db.session().commit()

        print("222222222222222222222222222222222222222222222222222")

        res = []
        res.append({"koti":joukkueet[0]["nimi"], "vieras":joukkueet[1]["nimi"], "laji":laji, "kerroin":2, "date_expire":t.date_expire})
    
        return res   

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
    kerroin = db.Column(db.DECIMAL, nullable=False)
    laji_id = db.Column(db.Integer, db.ForeignKey('laji.id'),
                           nullable=False)
    date_expire = db.Column(db.DateTime)
    active = db.Column(db.Boolean, nullable= False)
    


    def __init__(self, koti, vieras, laji, kerroin, date_expire):
        self.laji_id = laji
        self.koti = koti
        self.vieras = vieras
        self.kerroin = kerroin
        self.date_expire = date_expire
        self.active=True



    @staticmethod
    def haeMonivetoTapahtumat():
        
        #palauttaa listan monivetotapahtumista (3) with koti, vieras, laji, kerroin, date_expire
        #laittaa expiredeiksi tapahtumat, jotka menneet umpeen

        present = datetime.now()

        stmt = text("SELECT tapahtuma.id, koti, vieras, laji.nimi, kerroin, date_expire"
        " FROM tapahtuma, laji"
                     " WHERE laji.id = tapahtuma.laji_id AND active = 1"
                     )
        res = db.engine.execute(stmt)

        response = []
        
        for row in res:
            d = datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S.%f')
            
            
            if(d < present):
                print("------------------------------------------------")
                print(d)
                print(present)
                
                #setExpired(row[0])
                print(row[0])
                
               
                t = arvoUusiTapahtuma() #palautaa taulukon, jossa koti, vieras, laji, kerroin, date_expire

                response.append(t)
            else:
                print(d)
                print(present)
                print("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
                response.append({"koti":row[1], "vieras":row[2], "laji":row[3], "kerroin":row[4], "date_expire":row[5]})    
        
        while (len(response) < 3):
            t = arvoUusiTapahtuma()
            print(t)
            print("sssssssssssssssssssssssssssssssssss")
            response.append(t)
            print("ccccccccccccccccccccccccccccccccccccccccccccccc")
                

        print(response)
        return response
