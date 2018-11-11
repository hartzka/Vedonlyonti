from application import db
from application.models import Base

class Tapahtumaveto(Base):
    
    veikkaus = db.Column(db.String, nullable=False) #1, X, 2, 3-1, 2-2
    name = db.Column(db.String, nullable=False) #pitkaveto, tulosveto 
    veto_id = db.Column(db.Integer, db.ForeignKey('veto.id'),
                           nullable=False)
    tapahtuma_id = db.Column(db.Integer, db.ForeignKey('tapahtuma.id'),
                           nullable=False)


    def __init__(self, veikkaus, name, veto_id, tapahtuma_id):
        self.veikkaus = veikkaus
        self.name = name
        self.veto_id = veto_id
        self.tapahtuma_id = tapahtuma_id
        