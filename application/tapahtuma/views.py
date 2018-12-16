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
from application import app, db, login_manager, login_required
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
    Tapahtuma.do_veto_routines(False)
    tapahtumat = Tapahtuma.haeMonivetoTapahtumat(False)
    return render_template("tapahtumat/moniveto.html", 
    form=TapahtumaForm(), tapahtuma1=tapahtumat[0], tapahtuma2=tapahtumat[1],
    tapahtuma3=tapahtumat[2], tapahtuma4=tapahtumat[3], 
    tapahtuma5=tapahtumat[4], tapahtuma6=tapahtumat[5], live=0, sorted=0)

@app.route("/tapahtuma/tulosveto", methods=["GET"])
def tapahtumat_tulosveto():
    Tapahtuma.do_veto_routines(False)
    tapahtumat = Tapahtuma.haeTulosvetoTapahtumat()
    return render_template("tapahtumat/tulosveto.html", 
    form=TapahtumaForm(), tapahtuma1=tapahtumat[0], tapahtuma2=tapahtumat[1],
    tapahtuma3=tapahtumat[2], tapahtuma4=tapahtumat[3], 
    tapahtuma5=tapahtumat[4], tapahtuma6=tapahtumat[5], live=0)

@app.route("/tapahtuma/liveveto", methods=["GET"])
def tapahtumat_liveveto():
    Tapahtuma.do_veto_routines(True)
    tapahtumat = Tapahtuma.haeMonivetoTapahtumat(True)
    return render_template("tapahtumat/moniveto.html", 
    form=TapahtumaForm(), tapahtuma1=tapahtumat[0], tapahtuma2=tapahtumat[1],
    tapahtuma3=tapahtumat[2], tapahtuma4=tapahtumat[3], 
    tapahtuma5=tapahtumat[4], tapahtuma6=tapahtumat[5], live=1, sorted=0)

@app.route("/tapahtuma/moniveto/ready/<live>/<sorted>/", methods=["GET", "POST"])
def ready_moniveto(live, sorted):
    form = TapahtumaForm(request.form)
    t1 = form.moniveto1.data
    t2 = form.moniveto2.data
    t3 = form.moniveto3.data
    t4 = form.moniveto4.data
    t5 = form.moniveto5.data
    t6 = form.moniveto6.data
    
    if (t1=="-" and t2=="-" and t3=="-" and t4=="-" and t5=="-" and t6=="-"):
        return redirect(url_for("tapahtumat_moniveto"))
    if (int(sorted)==0):
        if (int(live)==1):
            monivedot = Tapahtuma.haeMonivetoTapahtumat(True)
        else:
            monivedot = Tapahtuma.haeMonivetoTapahtumat(False)
        
    else:
        if(int(live)==1):
            monivedot = Tapahtuma.haeMonivetoTapahtumat_groupByLaji(True)
        else:
            monivedot = Tapahtuma.haeMonivetoTapahtumat_groupByLaji(False)
        
    tapahtumat = []
    kerroin = 1
    if(t1!="-"):
        tapahtuma = monivedot[0]
        tama_kerroin = 1 #tamakerroin
        if (t1 == "1"):
            kerroin = kerroin*tapahtuma["kerroin1"]
            tama_kerroin = tapahtuma["kerroin1"]
        elif (t1 == "X"):
            kerroin = kerroin*tapahtuma["kerroinX"]
            tama_kerroin = tapahtuma["kerroinX"]
        elif (t1 == "2"):
            kerroin = kerroin*tapahtuma["kerroin2"]
            tama_kerroin = tapahtuma["kerroin2"]
        tama_kerroin = ("%.2f" % tama_kerroin)
        tapahtumat.append({"id":tapahtuma["id"], "koti":tapahtuma["koti"], "vieras":tapahtuma["vieras"], "laji":tapahtuma["laji"], "kerroin":tama_kerroin, "date_expire":tapahtuma["date_expire"], "veto":t1})
    if(t2!="-"):
        tapahtuma = monivedot[1]
        tama_kerroin = 1
        if (t2 == "1"):
            kerroin = kerroin*tapahtuma["kerroin1"]
            tama_kerroin = tapahtuma["kerroin1"]
        elif (t2 == "X"):
            kerroin = kerroin*tapahtuma["kerroinX"]
            tama_kerroin = tapahtuma["kerroinX"]
        elif (t2 == "2"):
            kerroin = kerroin*tapahtuma["kerroin2"]
            tama_kerroin = tapahtuma["kerroin2"]  
        tama_kerroin = ("%.2f" % tama_kerroin)  
        tapahtumat.append({"id":tapahtuma["id"], "koti":tapahtuma["koti"], "vieras":tapahtuma["vieras"], "laji":tapahtuma["laji"], "kerroin":tama_kerroin, "date_expire":tapahtuma["date_expire"], "veto":t2})
    if(t3!="-"):
        tapahtuma = monivedot[2]
        tama_kerroin = 1
        if (t3 == "1"):
            kerroin = kerroin*tapahtuma["kerroin1"]
            tama_kerroin = tapahtuma["kerroin1"]
        elif (t3 == "X"):
            kerroin = kerroin*tapahtuma["kerroinX"]
            tama_kerroin = tapahtuma["kerroinX"]
        elif (t3 == "2"):
            kerroin = kerroin*tapahtuma["kerroin2"]
            tama_kerroin = tapahtuma["kerroin2"]     
        tama_kerroin = ("%.2f" % tama_kerroin)
        tapahtumat.append({"id":tapahtuma["id"], "koti":tapahtuma["koti"], "vieras":tapahtuma["vieras"], "laji":tapahtuma["laji"], "kerroin":tama_kerroin, "date_expire":tapahtuma["date_expire"], "veto":t3})
    if(t4!="-"):
        tapahtuma = monivedot[3]
        tama_kerroin = 1
        if (t4 == "1"):
            kerroin = kerroin*tapahtuma["kerroin1"]
            tama_kerroin = tapahtuma["kerroin1"]
        elif (t4 == "X"):
            kerroin = kerroin*tapahtuma["kerroinX"]
            tama_kerroin = tapahtuma["kerroinX"]
        elif (t4 == "2"):
            kerroin = kerroin*tapahtuma["kerroin2"]
            tama_kerroin = tapahtuma["kerroin2"]     
        tama_kerroin = ("%.2f" % tama_kerroin)
        tapahtumat.append({"id":tapahtuma["id"], "koti":tapahtuma["koti"], "vieras":tapahtuma["vieras"], "laji":tapahtuma["laji"], "kerroin":tama_kerroin, "date_expire":tapahtuma["date_expire"], "veto":t4})
    if(t5!="-"):
        tapahtuma = monivedot[4]
        tama_kerroin = 1
        if (t5 == "1"):
            kerroin = kerroin*tapahtuma["kerroin1"]
            tama_kerroin = tapahtuma["kerroin1"]
        elif (t5 == "X"):
            kerroin = kerroin*tapahtuma["kerroinX"]
            tama_kerroin = tapahtuma["kerroinX"]
        elif (t5 == "2"):
            kerroin = kerroin*tapahtuma["kerroin2"]
            tama_kerroin = tapahtuma["kerroin2"] 
        tama_kerroin = ("%.2f" % tama_kerroin)
        tapahtumat.append({"id":tapahtuma["id"], "koti":tapahtuma["koti"], "vieras":tapahtuma["vieras"], "laji":tapahtuma["laji"], "kerroin":tama_kerroin, "date_expire":tapahtuma["date_expire"], "veto":t5})
    if(t6!="-"):
        tapahtuma = monivedot[5]
        tama_kerroin = 1
        if (t6 == "1"):
            kerroin = kerroin*tapahtuma["kerroin1"]
            tama_kerroin = tapahtuma["kerroin1"]
        elif (t6 == "X"):
            kerroin = kerroin*tapahtuma["kerroinX"]
            tama_kerroin = tapahtuma["kerroinX"]
        elif (t6 == "2"):
            kerroin = kerroin*tapahtuma["kerroin2"]
            tama_kerroin = tapahtuma["kerroin2"]
        tama_kerroin = ("%.2f" % tama_kerroin)       
        tapahtumat.append({"id":tapahtuma["id"], "koti":tapahtuma["koti"], "vieras":tapahtuma["vieras"], "laji":tapahtuma["laji"], "kerroin":tama_kerroin, "date_expire":tapahtuma["date_expire"], "veto":t6})
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
    veto = Veto(panos, moniveto.monivetokerroin, current_user.id)
    veto.id = veto_id
    
    tapahtumat = moniveto.monivetotapahtumat
    new_panos = int(int(panos)*(-1))
    if (current_user.rahat < int(panos)):
        return redirect(url_for("index"))
    db.session().add(veto)
    t = Tilitapahtuma("Peliosto", new_panos)
    t.account_id = current_user.id
    current_user.rahat = current_user.rahat - int(panos)
    db.session().add(t)
    db.session().commit()
   
    for tapahtuma in tapahtumat:
        tapahtuma_id = tapahtuma["id"]
        veikkaus = tapahtuma["veto"]
        tapahtumaveto = Tapahtumaveto(veikkaus, "moniveto", veto_id, tapahtuma_id)
        db.session().add(tapahtumaveto)
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
    veto = Veto(panos, kerroin, current_user.id)
    veto.id = veto_id
    
    tapahtumat = moniveto.monivetotapahtumat
    upanos = int(int(panos)*(-1))
    
    db.session().add(veto)
    tilitapahtuma = Tilitapahtuma("Peliosto", upanos)
    tilitapahtuma.account_id = current_user.id
    current_user.rahat = current_user.rahat - int(panos)
    db.session().add(tilitapahtuma)
    db.session().commit()

    tapahtumaveto = Tapahtumaveto(veikkaus, "tulosveto", veto_id, tapahtuma_id)
    db.session().add(tapahtumaveto)
    db.session().commit()
    return redirect(url_for("index"))

@app.route("/tapahtuma/moniveto/update/<veto_id>/", methods=["GET", "POST"])
def update_moniveto(veto_id):
    form = TapahtumaForm(request.form)
    t1 = form.moniveto1.data
    t2 = form.moniveto2.data
    t3 = form.moniveto3.data
    t4 = form.moniveto4.data
    t5 = form.moniveto5.data
    t6 = form.moniveto6.data
   
    if (t1=="-" or t2=="-" or t3=="-" or t4=="-" or t5=="-" or t6=="-"):
        return redirect(url_for("index"))
    monivedot = Tapahtuma.haeMonivetoTapahtumatByVetoId(veto_id) 
    tapahtumat = []
    kerroin = 1
    if(t1!="-"):
        tapahtuma = monivedot[0]
       
        if (t1 == "1"):
            kerroin = kerroin*tapahtuma["kerroin1"]
            
        elif (t1 == "X"):
            kerroin = kerroin*tapahtuma["kerroinX"]
            
        elif (t1 == "2"):
            kerroin = kerroin*tapahtuma["kerroin2"]
             
    if(t2!="-" and t2!=""):
        tapahtuma = monivedot[1]
      
        if (t2 == "1"):
            kerroin = kerroin*tapahtuma["kerroin1"]
            
        elif (t2 == "X"):
            kerroin = kerroin*tapahtuma["kerroinX"]
           
        elif (t2 == "2"):
            kerroin = kerroin*tapahtuma["kerroin2"]
           
    if(t3!="-" and t3!=""):
        tapahtuma = monivedot[2]
    
        if (t3 == "1"):
            kerroin = kerroin*tapahtuma["kerroin1"]
            
        elif (t3 == "X"):
            kerroin = kerroin*tapahtuma["kerroinX"]
           
        elif (t3 == "2"):
            kerroin = kerroin*tapahtuma["kerroin2"]
    
    if(t4!="-" and t4!=""):
        tapahtuma = monivedot[3]
    
        if (t4 =="1"):
            kerroin = kerroin*tapahtuma["kerroin1"]
            
        elif (t4 == "X"):
            kerroin = kerroin*tapahtuma["kerroinX"]
           
        elif (t4 == "2"):
            kerroin = kerroin*tapahtuma["kerroin2"]
    
    if(t5!="-" and t5!=""):
        tapahtuma = monivedot[4]
    
        if (t5 == "1"):
            kerroin = kerroin*tapahtuma["kerroin1"]
            
        elif (t5 == "X"):
            kerroin = kerroin*tapahtuma["kerroinX"]
           
        elif (t5 == "2"):
            kerroin = kerroin*tapahtuma["kerroin2"]

    if(t6!="-" and t6!=""):
        tapahtuma = monivedot[2]
    
        if (t6 == "1"):
            kerroin = kerroin*tapahtuma["kerroin1"]
            
        elif (t6 == "X"):
            kerroin = kerroin*tapahtuma["kerroinX"]
           
        elif (t6 == "2"):
            kerroin = kerroin*tapahtuma["kerroin2"]
    kerroin = ("%.2f" % float(kerroin))        

    stmt = text("UPDATE veto SET kerroin = :kerroin"
                    " WHERE id = :id"
                    ).params(kerroin=kerroin, id=veto_id)
    db.engine.execute(stmt)
    
    if (monivedot[0]["veikkaus"] != "-"):
        stmt = text("UPDATE tapahtumaveto SET veikkaus = :veikkaus"
                " WHERE id = :id"
                ).params(veikkaus=t1, id=monivedot[0]["tapahtumaveto_id"])
        db.engine.execute(stmt)
    if (monivedot[1]["veikkaus"] != "-"):
        stmt = text("UPDATE tapahtumaveto SET veikkaus = :veikkaus"
                " WHERE id = :id"
                ).params(veikkaus=t2, id=monivedot[1]["tapahtumaveto_id"])
        db.engine.execute(stmt)
    if (monivedot[2]["veikkaus"] != "-"):
        stmt = text("UPDATE tapahtumaveto SET veikkaus = :veikkaus"
                " WHERE id = :id"
                ).params(veikkaus=t3, id=monivedot[2]["tapahtumaveto_id"])
        db.engine.execute(stmt)
    if (monivedot[3]["veikkaus"] != "-"):
        stmt = text("UPDATE tapahtumaveto SET veikkaus = :veikkaus"
                " WHERE id = :id"
                ).params(veikkaus=t4, id=monivedot[3]["tapahtumaveto_id"])
        db.engine.execute(stmt)
    if (monivedot[4]["veikkaus"] != "-"):
        stmt = text("UPDATE tapahtumaveto SET veikkaus = :veikkaus"
                " WHERE id = :id"
                ).params(veikkaus=t5, id=monivedot[4]["tapahtumaveto_id"])
        db.engine.execute(stmt)
    if (monivedot[5]["veikkaus"] != "-"):
        stmt = text("UPDATE tapahtumaveto SET veikkaus = :veikkaus"
                " WHERE id = :id"
                ).params(veikkaus=t6, id=monivedot[5]["tapahtumaveto_id"])
        db.engine.execute(stmt)

    return redirect(url_for("index"))

@app.route("/tapahtuma/tulosveto/update/<veto_id>/", methods=["GET", "POST"])
def update_tulosveto(veto_id):
    form = TapahtumaForm(request.form)
    koti = form.tulosveto_koti.data
    vieras = form.tulosveto_vieras.data
    
    tulosvedot = Tapahtuma.haeMonivetoTapahtumatByVetoId(veto_id) 
    tapahtumat = []
    veikkaus = koti + "-" + vieras
    kerroin = Tapahtuma.haeTulosvetokerroin(tulosvedot[0]["tapahtuma_id"],veikkaus)
            
    kerroin = ("%.2f" % kerroin)        

    stmt = text("UPDATE veto SET kerroin = :kerroin"
                    " WHERE id = :id"
                    ).params(kerroin=kerroin, id=veto_id)
    db.engine.execute(stmt)
    
    if (tulosvedot[0]["veikkaus"] != "-"):
        stmt = text("UPDATE tapahtumaveto SET veikkaus = :veikkaus"
                " WHERE id = :id"
                ).params(veikkaus=veikkaus, id=tulosvedot[0]["tapahtumaveto_id"])
        db.engine.execute(stmt)

    return redirect(url_for("index"))

@app.route("/tapahtuma/moniveto/group/<live>/", methods=["GET", "POST"])
def group_moniveto_byLaji(live):
    if(int(live)==1):
        tapahtumat = Tapahtuma.haeMonivetoTapahtumat_groupByLaji(True)
    else:
        tapahtumat = Tapahtuma.haeMonivetoTapahtumat_groupByLaji(False)
    return render_template("tapahtumat/moniveto.html", 
    form=TapahtumaForm(), tapahtuma1=tapahtumat[0], tapahtuma2=tapahtumat[1],
    tapahtuma3=tapahtumat[2], tapahtuma4=tapahtumat[3], 
    tapahtuma5=tapahtumat[4], tapahtuma6=tapahtumat[5], live=live, sorted=1)
    
@app.route("/tapahtuma/tulosveto/group/", methods=["GET", "POST"])
def group_tulosveto_byLaji():
    tapahtumat = Tapahtuma.haeTulosvetoTapahtumat_groupByLaji()
    return render_template("tapahtumat/tulosveto.html", 
    form=TapahtumaForm(), tapahtuma1=tapahtumat[0], tapahtuma2=tapahtumat[1],
    tapahtuma3=tapahtumat[2], tapahtuma4=tapahtumat[3], 
    tapahtuma5=tapahtumat[4], tapahtuma6=tapahtumat[5])
    
  