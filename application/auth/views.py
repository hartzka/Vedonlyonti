from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user

from application import app, db
from application.auth.models import User
from application.auth.forms import LoginForm
import random

@app.route("/auth/login", methods = ["GET", "POST"])
def auth_login():
    print(max(float("%.2f" % (0.2 + random.random()*0.4 - 0.2)),1.01))
    if request.method == "GET":
        return render_template("auth/loginform.html", form = LoginForm())

    form = LoginForm(request.form)
    # mahdolliset validoinnit

    user = User.query.filter_by(username=form.username.data, password=form.password.data).first()
    if not user:
        return render_template("auth/loginform.html", form = form,
                               error = "Käyttäjätunnusta tai salasanaa ei löydy")

    login_user(user)
    return redirect(url_for("index"))    

@app.route("/auth/logout")
def auth_logout():
    logout_user()
    return redirect(url_for("index")) 

@app.route("/auth/new", methods = ["GET", "POST"])
def auth_new():
    if request.method == "GET":
        return render_template("auth/new.html", form=LoginForm())

    form = LoginForm(request.form)
    if not form.validate():
        return render_template("auth/new.html", form = form, error = "Minimipituus 2")

    user = User.query.filter_by(username=form.username.data, password=form.password.data).first()
    if not user:
        new_user = User(form.name.data,form.username.data,form.password.data)

        db.session().add(new_user)
        db.session().commit()
        return redirect(url_for("index"))  
    
    return render_template("auth/new.html", form = LoginForm())
