from flask import render_template, request, redirect, url_for
from flask_login import current_user
from sqlalchemy.sql import text
from application import app, db, login_manager
from application.auth.models import User

@app.route("/vedot", methods=["GET"])
def vedot_index():
    return render_template("vedot/vedot.html", vedot=User.find_vedot_byUser(current_user.id))

@app.route("/vedot/<veto_id>/", methods=["POST"])
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
