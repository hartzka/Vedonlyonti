from flask import render_template, request, redirect, url_for
from flask_login import current_user
from sqlalchemy.sql import text
from application import app, db, login_manager, login_required
from application.tilitapahtuma.models import Tilitapahtuma
from application.tilitapahtuma.forms import TilisiirtoForm
from application.tilitapahtuma.forms import PankkisiirtoForm
from application.auth.models import User

@app.route("/tilitapahtumat/", methods=["GET","POST"])
@login_required(role="ADMIN")
def tilitapahtumat_index():
    return render_template("tilitapahtumat/new.html", tilisiirtoform = TilisiirtoForm(), pankkisiirtoform = PankkisiirtoForm(), tilitapahtumat = User.find_tilitapahtumat_byUser(current_user.id))
    
@app.route("/tilitapahtumat/new/")
def tilitapahtumat_form():
    return render_template("tilitapahtumat/new.html", tilisiirtoform = TilisiirtoForm(), pankkisiirtoform = PankkisiirtoForm())

@app.route("/tilitapahtumat/delete/", methods=["POST"])
def delete_tilitapahtumat():
    stmt = text("DELETE FROM tilitapahtuma")
    db.engine.execute(stmt)
    return redirect(url_for("tilitapahtumat_index"))

@app.route("/tilitapahtumat/<tilitapahtuma_id>/", methods=["POST"])
def add_to_game_account(tilitapahtuma_id):

    t = Tilitapahtuma.query.get(tilitapahtuma_id)
    if t.account_id != current_user.id:
        return login_manager.unauthorized()
    
    return redirect(url_for("tilitapahtumat_index"))



@app.route("/tilitapahtumat/tilisiirto", methods=["POST"])
def tilitapahtuma_pelitilille():
    form = TilisiirtoForm(request.form)

    if not form.validate() or form.tilisiirto.data <= 0:

        return render_template("tilitapahtumat/new.html", tilisiirtoform = form, pankkisiirtoform = PankkisiirtoForm(),
        tilitapahtumat = User.find_tilitapahtumat_byUser(current_user.id),error = "Anna positiivinen kokonaisluku, max 10000")

    t = Tilitapahtuma("Siirto pelitilille", form.tilisiirto.data)
    t.account_id = current_user.id
    current_user.rahat += form.tilisiirto.data

    db.session().add(t)
    db.session().commit()
    
    return redirect(url_for("tilitapahtumat_index"))

@app.route("/tilitapahtumat/pankkisiirto", methods=["POST"])
def tilitapahtuma_pankkitilille():
    form = PankkisiirtoForm(request.form)

    if not form.validate() or form.pankkisiirto.data > current_user.rahat or form.pankkisiirto.data <= 0:
        return render_template("tilitapahtumat/new.html", pankkisiirtoform = form, tilisiirtoform = TilisiirtoForm(), 
        tilitapahtumat = User.find_tilitapahtumat_byUser(current_user.id),error = "Anna positiivinen kokonaisluku, max 10000")

    t = Tilitapahtuma("Siirto pankkitilille", form.pankkisiirto.data*(-1))
    t.account_id = current_user.id
    current_user.rahat -= form.pankkisiirto.data

    db.session().add(t)
    db.session().commit()
    
    return redirect(url_for("tilitapahtumat_index"))