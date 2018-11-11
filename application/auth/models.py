from application import db
from application.models import Base
from sqlalchemy.sql import text

class User(Base):

    __tablename__ = "account"
  
    name = db.Column(db.String(144), nullable=False)
    username = db.Column(db.String(144), nullable=False)
    password = db.Column(db.String(144), nullable=False)
    rahat = db.Column(db.DECIMAL, nullable=False)

    def __init__(self, name, username, password):
        self.name = name
        self.username = username
        self.password = password
        self.rahat = 0
  
    def get_id(self):
        return self.id

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def roles(self):
        return ["ADMIN"]

    @staticmethod
    def find_tilitapahtumat_byUser(id):
        stmt = text("SELECT siirto, tilitapahtuma.date_created, account_id FROM tilitapahtuma"
                     " LEFT JOIN Account ON tilitapahtuma.account_id = Account.id"
                     )
        res = db.engine.execute(stmt)

        response = []
        for row in res:
            if(row[2] == id):
                response.append({"siirto":row[0], "date_created":row[1]})

        return response
    
