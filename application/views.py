from flask import render_template
from application import app
from datetime import datetime

@app.route('/')
def index():
    d = str(datetime.now())
    d = d[:16]
    t = datetime.strptime(d, '%Y-%m-%d %H:%M')
    t = str(t)[:16]
    return render_template("index.html", time=t)
