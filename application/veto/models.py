from application import db
from application.models import Base
from sqlalchemy.sql import text
from datetime import datetime

class Veto(Base):
    
    panos = db.Column(db.Integer, nullable=False)
    kerroin = db.Column(db.DECIMAL, nullable=False)
    voitto = db.Column(db.DECIMAL, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'),
                           nullable=False)


    def __init__(self, panos, kerroin, account_id):
        self.panos = panos
        self.kerroin = kerroin
        self.account_id = account_id
        self.voitto = 0

    
    @staticmethod
    def haeVetoid():
        stmt = text("SELECT max(id)"
                    " FROM veto"
        )
        res = db.engine.execute(stmt)
        
        uid = 0
        for row in res:
            if type(row[0]) == int:
                uid = row[0]

        return (uid+1)

    @staticmethod
    def haePoistettavat():
        tapahtumat = []
        
        stmt = text("SELECT id FROM tapahtuma WHERE active = 0"
        " AND id NOT IN (SELECT tapahtuma_id FROM tapahtumaveto)"
        " AND id NOT IN (SELECT tapahtuma_id FROM tapahtumajoukkue)")
        res = db.engine.execute(stmt)
        for row in res:
            tapahtumat.append(row[0])
        
        return tapahtumat
    