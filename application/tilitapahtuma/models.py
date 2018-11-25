from application import db
from application.models import Base

class Tilitapahtuma(Base):
    
    siirto = db.Column(db.DECIMAL, nullable=False)
    info = db.Column(db.String, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'),
                           nullable=False)


    def __init__(self, info, siirto):
        self.info = info
        self.siirto = siirto
        