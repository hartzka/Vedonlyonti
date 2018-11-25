from application import db
from application.models import Base

class Tapahtumajoukkue(Base):
    
    pisteet = db.Column(db.Integer)
    koti = db.Column(db.Boolean, nullable=False)
    attack = db.Column(db.Integer, nullable=False)
    defence = db.Column(db.Integer, nullable=False)
    tactic = db.Column(db.Integer, nullable=False)
    joukkue_id = db.Column(db.Integer, db.ForeignKey('joukkue.id'),
                           nullable=False)
    tapahtuma_id = db.Column(db.Integer, db.ForeignKey('tapahtuma.id'),
                           nullable=False)

    def __init__(self, koti, attack, defence, tactic, joukkue, tapahtuma):
        self.pisteet = -1
        self.joukkue_id = joukkue
        self.tapahtuma_id = tapahtuma
        self.attack = attack
        self.defence = defence
        self.tactic = tactic
        self.koti = koti


    