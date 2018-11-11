from application import db
from application.models import Base

class Veto(Base):
    
    panos = db.Column(db.Integer, nullable=False)
    kerroin = db.Column(db.Integer, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'),
                           nullable=False)


    def __init__(self, panos, kerroin, account_id):
        self.panos = panos
        self.kerroin = kerroin
        self.account_id = account_id
        