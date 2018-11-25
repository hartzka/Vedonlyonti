from application import db
from application.models import Base
from sqlalchemy.sql import text

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
        
    
    @staticmethod
    def haeVedot(veto_id):
        stmt = text("SELECT id, veikkaus, name, tapahtuma_id FROM tapahtumaveto"
                     " WHERE tapahtumaveto.veto_id = :id"
                     ).params(id=veto_id)
        res = db.engine.execute(stmt)

        response = []
        for row in res:
            response.append({"id":row[0], "veikkaus":row[1], "name":row[2], "tapahtuma_id":row[3]})
        return response