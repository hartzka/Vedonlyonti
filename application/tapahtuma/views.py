from flask import render_template, request, redirect, url_for
from flask_login import current_user
from application.veto.models import Veto
from application.tapahtumaveto.models import Tapahtumaveto
from datetime import datetime
import random
from application.tapahtuma.forms import TapahtumaForm
from sqlalchemy.sql import text
from application.tapahtuma.models import Tapahtuma
from application.tapahtumajoukkue.models import Tapahtumajoukkue
from application.tapahtuma.forms import Choices
from application import app, db, login_manager
from application.auth.models import User
from application.tilitapahtuma.models import Tilitapahtuma



class Moniveto:
    monivetotapahtumat = [] #events
    monivetokerroin = 1

    def __init__(self):
        self.monivetotapahtumat = [] #events
        self.monivetokerroin = 1

    
    def setMonivetotapahtumat(self,mv):
        self.monivetotapahtumat = mv

    def setMonivetokerroin(self,mv):
        self.monivetokerroin = mv

    
    
moniveto = Moniveto()

@app.route("/tapahtuma/moniveto", methods=["GET"])
def tapahtumat_moniveto():
    
    present = datetime.now()

    poistettavat = Veto.haePoistettavat() #poistettavat tapahtumat, jotka ei liity vetoihin
    for tid in poistettavat:
        stmt = text("DELETE FROM tapahtuma WHERE id = :id"
        ).params(id = tid)
        db.engine.execute(stmt)

    stmt = text("SELECT id, date_expire FROM tapahtuma WHERE active = 1")
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
            while (home_goals < 0):
                home_goals = int(random.gauss(2+(response[0]["attack"]-response[1]["defence"])/10, 3)) + int(random.gauss(response[0]["tactic"]/100, 1))

            away_goals = -1
            while (away_goals < 0):
                away_goals = int(random.gauss(2+(response[1]["attack"]-response[0]["defence"])/10, 3)) + int(random.gauss(response[1]["tactic"]/100, 1))

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

    vedot = User.haeVedot(current_user.id)
    for veto in vedot:
        oikein = True
        tvedot = Tapahtumaveto.haeVedot(veto["id"])
        if (len(tvedot) == 0):
            oikein = False
        for tveto in tvedot:
            tulos = Tapahtuma.haeTulos(tveto["tapahtuma_id"])
            if (tulos == "kesken" or tulos == ""):
                oikein = False
                break
            print(tulos)
            print("Tulos")
            
            if(tveto["name"] == "moniveto"):
                koti = 0
                vieras = 0
                if (tulos[1]=="-"):
                    koti = int(tulos[0])
                    if (len(tulos) > 3):
                        vieras = int(tulos[2:3])
                    else:
                        vieras = int(tulos[2])    
                else:
                    koti = int(tulos[0:1])    
                    if (len(tulos) > 4):
                        vieras = int(tulos[3:4])
                    else:
                        vieras = int(tulos[3])  
                veikkaus = tveto["veikkaus"]
                print(veikkaus)
                print("veikkaus")
                
                if (koti > vieras and veikkaus != "1"):
                    oikein = False
                    break
                elif (koti < vieras and veikkaus != "2"):
                    oikein = False
                    break    
                elif (koti == vieras and veikkaus != "X"):
                    oikein = False
                    break    
        if (oikein == True):
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
    
    for i in range (3):
        tapahtumat = Tapahtuma.haeMonivetoTapahtuma()
        if (len(tapahtumat) == 0):
            break
        if (tapahtumat[0][0]["old"] == -7):
            stmt2 = text("DELETE FROM tapahtumajoukkue")
            db.engine.execute(stmt2)
            tapahtumat = Tapahtuma.haeMonivetoTapahtuma()
       
        row = tapahtumat[0][0]
        tj1 = row["tj1"]
        tj2 = row["tj2"]
        t = Tapahtuma(row["koti"], row["vieras"],
        row["laji"], row["kerroin1"], row["kerroinX"], row["kerroin2"],
        row["date_expire"], True)
        t.id = row["id"]
        db.session().add(t)
        db.session().commit()
        db.session().add(tj1)
        db.session().add(tj2)
        db.session().commit()
        stmt = text("UPDATE tapahtuma SET active = 0 WHERE id = :id"
                     ).params(id=row["old"])
        db.engine.execute(stmt)
        
    tapahtumat = Tapahtuma.haeMonivetoTapahtumat()
    return render_template("tapahtumat/moniveto.html", 
    form=TapahtumaForm(), tapahtuma1=tapahtumat[0], tapahtuma2=tapahtumat[1],
    tapahtuma3=tapahtumat[2])
    

@app.route("/tapahtuma/moniveto/ready", methods=["GET", "POST"])
def ready_moniveto():
    form = TapahtumaForm(request.form)
    #form.process()
    t1 = form.veto1.data
    t2 = form.veto2.data
    t3 = form.veto3.data
    
    if (t1=="-" and t2=="-" and t3=="-"):
        return redirect(url_for("tapahtumat_moniveto"))
    tap = Tapahtuma.haeMonivetoTapahtumat()
    tapahtumat = []
    kerroin = 1
    if(t1!="-"):
        t = tap[0]
        tkerroin = 1 #tamakerroin
        if (t1 == "1"):
            kerroin = kerroin*t["kerroin1"]
            tkerroin = t["kerroin1"]
        elif (t1 == "X"):
            kerroin = kerroin*t["kerroinX"]
            tkerroin = t["kerroinX"]
        elif (t1 == "2"):
            kerroin = kerroin*t["kerroin2"]
            tkerroin = t["kerroin2"]        
        tapahtumat.append({"id":t["id"], "koti":t["koti"], "vieras":t["vieras"], "laji":t["laji"], "kerroin":tkerroin, "date_expire":t["date_expire"], "veto":t1})
    if(t2!="-"):
        t = tap[1]
        tkerroin = 1
        if (t2 == "1"):
            kerroin = kerroin*t["kerroin1"]
            tkerroin = t["kerroin1"]
        elif (t2 == "X"):
            kerroin = kerroin*t["kerroinX"]
            tkerroin = t["kerroinX"]
        elif (t2 == "2"):
            kerroin = kerroin*t["kerroin2"]
            tkerroin = t["kerroin2"]    
        tapahtumat.append({"id":t["id"], "koti":t["koti"], "vieras":t["vieras"], "laji":t["laji"], "kerroin":tkerroin, "date_expire":t["date_expire"], "veto":t2})
    if(t3!="-"):
        t = tap[2]
        tkerroin = 1
        if (t3 == "1"):
            kerroin = kerroin*t["kerroin1"]
            tkerroin = t["kerroin1"]
        elif (t3 == "X"):
            kerroin = kerroin*t["kerroinX"]
            tkerroin = t["kerroinX"]
        elif (t3 == "2"):
            kerroin = kerroin*t["kerroin2"]
            tkerroin = t["kerroin2"]
        tkerroin = ("%.2f" % tkerroin)
        kerroin = ("%.2f" % kerroin)        
        tapahtumat.append({"id":t["id"], "koti":t["koti"], "vieras":t["vieras"], "laji":t["laji"], "kerroin":tkerroin, "date_expire":t["date_expire"], "veto":t3})
    
    moniveto.setMonivetokerroin(kerroin)
    moniveto.setMonivetotapahtumat(tapahtumat)
    return render_template("tapahtumat/moniveto2.html", tapahtumat=tapahtumat,kerroin=kerroin, form=TapahtumaForm())


@app.route("/tapahtuma/moniveto/new", methods=["GET", "POST"])
def create_moniveto():
    form = TapahtumaForm(request.form)
    panos = form.panos.data
    
    veto_id = Veto.haeVetoid()
    v = Veto(panos, moniveto.monivetokerroin, current_user.id)
    v.id = veto_id
    db.session().add(v)
    tapahtumat = moniveto.monivetotapahtumat
    upanos = int(int(panos)*(-1))
    t = Tilitapahtuma("Peliosto", upanos)
    t.account_id = current_user.id
    current_user.rahat = current_user.rahat - int(panos)
    db.session().add(t)
    db.session().commit()
   
    for tapahtuma in tapahtumat:
        tapahtuma_id = tapahtuma["id"]
        veikkaus = tapahtuma["veto"]
        tv = Tapahtumaveto(veikkaus, "moniveto", veto_id, tapahtuma_id)
        db.session().add(tv)
    db.session().commit()
    return redirect(url_for("index"))
  