from flask import render_template, request, redirect, url_for
from flask_login import current_user
from datetime import datetime
import random
from application.tapahtuma.models import Tapahtuma

from application import app, db, login_manager
from application.auth.models import User

@app.route("/tapahtuma/moniveto/", methods=["GET"])
def tapahtumat_moniveto():
    
    present = datetime.now()
    print(present.month)
    print(present.minute)
    print(present.second)
    present_user = current_user.date_created
    if (present_user < present):
        print(present_user)
        print("aatama")
    for i in range (100):
        print(random.gauss(1.0, 2.0))
    return render_template("tapahtumat/moniveto.html", tapahtumat=Tapahtuma.haeMonivetoTapahtumat())
    