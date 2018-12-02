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
from application.tapahtuma.forms import ChoicesMoniveto, ChoicesTulosveto
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
            elif(tveto["name"] == "tulosveto"):
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
                vkoti = 0 #veikkauskoti
                vvieras = 0 #veikkausvieras
                if (veikkaus[1]=="-"):
                    vkoti = int(veikkaus[0])
                    if (len(veikkaus) > 3):
                        vvieras = 10
                    else:
                        vvieras = int(veikkaus[2])
                else:
                    vvkoti = 10
                    if (len(veikkaus) > 5):
                        vvieras = 10
                    else:
                        vvieras = int(veikkaus[4])
                if(koti >= 10 and vkoti == 10 and vieras==vvieras):
                    break
                elif(vieras >= 10 and vvieras == 10 and koti==vkoti):
                    break
                elif(koti >= 10 and vkoti == 10 and vieras >= 10 and vvieras == 10):
                    break
                elif (koti != vkoti):
                    oikein = False
                    break
                elif (vieras != vvieras):
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

@app.route("/tapahtuma/tulosveto", methods=["GET"])
def tapahtumat_tulosveto():
    
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
            elif(tveto["name"] == "tulosveto"):
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
                vkoti = 0 #veikkauskoti
                vvieras = 0 #veikkausvieras
                if (veikkaus[1]=="-"):
                    vkoti = int(veikkaus[0])
                    if (len(veikkaus) > 3):
                        vvieras = 10
                    else:
                        vvieras = int(veikkaus[2])
                else:
                    vvkoti = 10
                    if (len(veikkaus) > 5):
                        vvieras = 10
                    else:
                        vvieras = int(veikkaus[4])
                if(koti >= 10 and vkoti == 10 and vieras==vvieras):
                    break
                elif(vieras >= 10 and vvieras == 10 and koti==vkoti):
                    break
                elif(koti >= 10 and vkoti == 10 and vieras >= 10 and vvieras == 10):
                    break
                elif (koti != vkoti):
                    oikein = False
                    break
                elif (vieras != vvieras):
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
    return render_template("tapahtumat/tulosveto.html", 
    form=TapahtumaForm(), tapahtuma1=tapahtumat[0], tapahtuma2=tapahtumat[1],
    tapahtuma3=tapahtumat[2])
        

@app.route("/tapahtuma/moniveto/ready", methods=["GET", "POST"])
def ready_moniveto():
    form = TapahtumaForm(request.form)
    t1 = form.moniveto1.data
    t2 = form.moniveto2.data
    t3 = form.moniveto3.data
    
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
    kerroin = ("%.2f" % float(kerroin))
    return render_template("tapahtumat/moniveto2.html", tapahtumat=tapahtumat,kerroin=kerroin, form=TapahtumaForm())

@app.route("/tapahtuma/tulosveto/ready/<tapahtuma_id>/", methods=["GET", "POST"])
def ready_tulosveto(tapahtuma_id):
    tapahtuma = Tapahtuma.haeTulosvetoTapahtumaById(tapahtuma_id)[0]
    return render_template("tapahtumat/tulosveto2.html", tapahtuma=tapahtuma, form=TapahtumaForm())


@app.route("/tapahtuma/moniveto/new", methods=["GET", "POST"])
def create_moniveto():
    form = TapahtumaForm(request.form)
    panos = form.panos.data
    
    veto_id = Veto.haeVetoid()
    v = Veto(panos, moniveto.monivetokerroin, current_user.id)
    v.id = veto_id
    
    tapahtumat = moniveto.monivetotapahtumat
    upanos = int(int(panos)*(-1))
    if (current_user.rahat < int(panos)):
        return redirect(url_for("index"))
    db.session().add(v)
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

@app.route("/tapahtuma/tulosveto/new/<tapahtuma_id>/", methods=["GET", "POST"])
def create_tulosveto(tapahtuma_id):
    form = TapahtumaForm(request.form)
    panos = form.panos.data
    if (current_user.rahat < int(panos)):
        return redirect(url_for("index"))
    veikkaus = form.tulosveto_koti.data + "-" + form.tulosveto_vieras.data
    kerroin = Tapahtuma.haeTulosvetokerroin(tapahtuma_id,veikkaus)
    veto_id = Veto.haeVetoid()
    v = Veto(panos, kerroin, current_user.id)
    v.id = veto_id
    
    tapahtumat = moniveto.monivetotapahtumat
    upanos = int(int(panos)*(-1))
    
    db.session().add(v)
    t = Tilitapahtuma("Peliosto", upanos)
    t.account_id = current_user.id
    current_user.rahat = current_user.rahat - int(panos)
    db.session().add(t)
    db.session().commit()

    tv = Tapahtumaveto(veikkaus, "tulosveto", veto_id, tapahtuma_id)
    db.session().add(tv)
    db.session().commit()
    return redirect(url_for("index"))

@app.route("/tapahtuma/moniveto/update/<veto_id>/", methods=["GET", "POST"])
def update_moniveto(veto_id):
    form = TapahtumaForm(request.form)
    t1 = form.moniveto1.data
    t2 = form.moniveto2.data
    t3 = form.moniveto3.data
   
    if (t1=="-" or t2=="-" or t3=="-"):
        return redirect(url_for("index"))
    tap = Tapahtuma.haeMonivetoTapahtumatByVetoId(veto_id) 
    tapahtumat = []
    kerroin = 1
    if(t1!="-"):
        t = tap[0]
       
        if (t1 == "1"):
            kerroin = kerroin*t["kerroin1"]
            
        elif (t1 == "X"):
            kerroin = kerroin*t["kerroinX"]
            
        elif (t1 == "2"):
            kerroin = kerroin*t["kerroin2"]
             
    if(t2!="-" and t2!=""):
        t = tap[1]
      
        if (t2 == "1"):
            kerroin = kerroin*t["kerroin1"]
            
        elif (t2 == "X"):
            kerroin = kerroin*t["kerroinX"]
           
        elif (t2 == "2"):
            kerroin = kerroin*t["kerroin2"]
           
    if(t3!="-" and t3!=""):
        t = tap[2]
    
        if (t3 == "1"):
            kerroin = kerroin*t["kerroin1"]
            
        elif (t3 == "X"):
            kerroin = kerroin*t["kerroinX"]
           
        elif (t3 == "2"):
            kerroin = kerroin*t["kerroin2"]
            
        kerroin = ("%.2f" % kerroin)        

    stmt = text("UPDATE veto SET kerroin = :kerroin"
                    " WHERE id = :id"
                    ).params(kerroin=kerroin, id=veto_id)
    db.engine.execute(stmt)
    
    if (tap[0]["veikkaus"] != "-"):
        stmt = text("UPDATE tapahtumaveto SET veikkaus = :veikkaus"
                " WHERE id = :id"
                ).params(veikkaus=t1, id=tap[0]["tapahtumaveto_id"])
        db.engine.execute(stmt)
    if (tap[1]["veikkaus"] != "-"):
        stmt = text("UPDATE tapahtumaveto SET veikkaus = :veikkaus"
                " WHERE id = :id"
                ).params(veikkaus=t2, id=tap[1]["tapahtumaveto_id"])
        db.engine.execute(stmt)
    if (tap[2]["veikkaus"] != "-"):
        stmt = text("UPDATE tapahtumaveto SET veikkaus = :veikkaus"
                " WHERE id = :id"
                ).params(veikkaus=t3, id=tap[2]["tapahtumaveto_id"])
        db.engine.execute(stmt)

    return redirect(url_for("index"))

@app.route("/tapahtuma/tulosveto/update/<veto_id>/", methods=["GET", "POST"])
def update_tulosveto(veto_id):
    form = TapahtumaForm(request.form)
    koti = form.tulosveto_koti.data
    vieras = form.tulosveto_vieras.data
    
    tap = Tapahtuma.haeMonivetoTapahtumatByVetoId(veto_id) 
    tapahtumat = []
    veikkaus = koti + "-" + vieras
    kerroin = Tapahtuma.haeTulosvetokerroin(tap[0]["tapahtuma_id"],veikkaus)
            
    kerroin = ("%.2f" % kerroin)        

    stmt = text("UPDATE veto SET kerroin = :kerroin"
                    " WHERE id = :id"
                    ).params(kerroin=kerroin, id=veto_id)
    db.engine.execute(stmt)
    
    if (tap[0]["veikkaus"] != "-"):
        stmt = text("UPDATE tapahtumaveto SET veikkaus = :veikkaus"
                " WHERE id = :id"
                ).params(veikkaus=veikkaus, id=tap[0]["tapahtumaveto_id"])
        db.engine.execute(stmt)

    return redirect(url_for("index"))
  