from flask import render_template, request, redirect, url_for
from flask_login import current_user
from sqlalchemy.sql import text
from application import app, db, login_manager
from application.auth.models import User
from application.tapahtuma.forms import TapahtumaForm
from application.tapahtuma.models import Tapahtuma

@app.route("/vedot", methods=["GET"])
def vedot_index():
    return render_template("vedot/vedot.html", vedot=User.find_vedot_byUser(current_user.id))

@app.route("/vedot/delete/<veto_id>/", methods=["POST"])
def delete_veto(veto_id):

    tapahtumavedot = []
    stmt = text("SELECT id, tapahtuma_id, veto_id FROM tapahtumaveto WHERE veto_id = :id"
    ).params(id=veto_id)
    res = db.engine.execute(stmt)
    for row in res:
        tapahtumavedot.append(row[0])
    
    for t_id in tapahtumavedot:
        stmt2 = text("DELETE FROM tapahtumaveto WHERE id = :id"
        ).params(id=t_id)
        db.engine.execute(stmt2)

    stmt3 = text("DELETE FROM veto WHERE id = :id"
    ).params(id=veto_id)
    db.engine.execute(stmt3)

    return redirect(url_for("vedot_index"))

@app.route("/vedot/update/<veto_id>/<name>/", methods=["POST"])
def update_veto(veto_id, name):
    #vedot=User.find_vedot_byUser(current_user.id, veto_id)
    tapahtumat = Tapahtuma.haeMonivetoTapahtumatByVetoId(veto_id)
    print(tapahtumat)
    form = TapahtumaForm()
    if(name=="moniveto"):
        form.moniveto1.default = tapahtumat[0]["veikkaus"]
        form.moniveto2.default = tapahtumat[1]["veikkaus"]
        form.moniveto3.default = tapahtumat[2]["veikkaus"]
        form.process()
        return render_template("tapahtumat/moniveto_update.html", form=form, 
        tapahtuma1=tapahtumat[0], tapahtuma2=tapahtumat[1],
        tapahtuma3=tapahtumat[2], veto_id=veto_id)
    elif(name=="tulosveto"):
        veikkaus = tapahtumat[0]["veikkaus"]
        vkoti = "" #veikkauskoti
        vvieras = "" #veikkausvieras
        if (veikkaus[1]=="-"):
            vkoti = str(veikkaus[0])
            if (len(veikkaus) > 3):
                vvieras = "10+"
            else:
                vvieras = str(veikkaus[2])
        else:
            vkoti = "10+"
            if (len(veikkaus) > 5):
                vvieras = "10+"
            else:
                vvieras = str(veikkaus[4])
        form.tulosveto_koti.default = vkoti
        form.tulosveto_vieras.default = vvieras
        form.process()
        return render_template("tapahtumat/tulosveto_update.html", form=form, 
        tapahtuma=tapahtumat[0], veto_id=veto_id)