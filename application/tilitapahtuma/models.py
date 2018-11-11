from application import db
from application.models import Base

class Tilitapahtuma(Base):
    
    siirto = db.Column(db.Integer, nullable=False)

    account_id = db.Column(db.Integer, db.ForeignKey('account.id'),
                           nullable=False)


    def __init__(self, siirto):
        self.siirto = siirto
        