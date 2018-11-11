from application import db
from application.models import Base

class Joukkue(Base):
    
    nimi = db.Column(db.String, nullable=False)
    attack = db.Column(db.Integer, nullable=False)
    defence = db.Column(db.Integer, nullable=False)
    tactic = db.Column(db.Integer, nullable=False)
    laji_id = db.Column(db.Integer, db.ForeignKey('laji.id'),
                           nullable=False)


    def __init__(self, nimi, attack, defence, tactic, laji):
        self.laji_id = laji
        self.nimi = nimi
        self.attack = attack
        self.defence = defence
        self.tactic = tactic