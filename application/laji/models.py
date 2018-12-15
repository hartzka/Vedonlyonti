from application import db
from application.models import Base
from sqlalchemy.sql import text

class Laji(Base):
    
    nimi = db.Column(db.String, nullable=False)
    
    def __init__(self, nimi):
        self.nimi = nimi

    @staticmethod
    def haeLaji(laji_id=0):
        stmt = text("SELECT nimi"
                    " FROM laji"
                     " WHERE id = :id"
                     ).params(id = laji_id)
        res = db.engine.execute(stmt)
        response = []
        
        for row in res:
            response.append({"nimi":row[0]})

        return response[0]["nimi"]     