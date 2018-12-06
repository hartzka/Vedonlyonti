from application import db
from application.models import Base
from flask_login import current_user
from sqlalchemy.sql import text

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

    
    @staticmethod
    def findJoukkueetInVedot():
        stmt = text("select koti, vieras from tapahtuma"
        " inner join tapahtumaveto on tapahtumaveto.tapahtuma_id=tapahtuma.id"
        " inner join veto on tapahtumaveto.veto_id=veto.id"
        " inner join account on veto.account_id = :id"
        " group by tapahtuma.koti, tapahtuma.vieras"
                     ).params(id = current_user.id)
        res = db.engine.execute(stmt)
        response = []
        
        for row in res:
            if row[0] not in response:
                response.append(row[0])
            if row[1] not in response:
                response.append(row[1])
        response = sorted(response)
        return response  