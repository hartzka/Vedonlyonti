from application import db
from application.models import Base
from sqlalchemy.sql import text
from datetime import datetime, timedelta

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

    def getRahat(self):
        return ("%.2f" % self.rahat)    

    @staticmethod
    def find_tilitapahtumat_byUser(user_id):
        stmt = text("SELECT siirto, tilitapahtuma.date_created, account_id, info FROM tilitapahtuma"
                     " WHERE tilitapahtuma.account_id = :id"
                     ).params(id=user_id)
        res = db.engine.execute(stmt)

        response = []
        for row in res:
            date = str(datetime.strptime(str(row[1]), '%Y-%m-%d %H:%M:%S.%f'))
            date = date[0:16]
            response.append({"siirto":row[0], "date_created":date, "info":row[3]})

        return response

    @staticmethod
    def haeVedot(user_id):
        stmt = text("SELECT id, panos, kerroin FROM veto"
                     " WHERE veto.account_id = :id"
                     ).params(id=user_id)
        res = db.engine.execute(stmt)

        response = []
        for row in res:
            response.append({"id":row[0], "panos":row[1], "kerroin":row[2]})
        return response    

    @staticmethod
    def find_vedot_byUser(user_id):
        stmt = text("SELECT id, panos, kerroin, voitto FROM veto"
                     " WHERE veto.account_id = :id"
                     ).params(id=user_id)
        res = db.engine.execute(stmt)

        response = []
        for row in res:
            vedot = []
            row3 = []
            active = 1
            non_actives = False
            actives = False
            kerroin = row[2]
            kerroin = ("%.2f" % kerroin)
            stmt2 = text("SELECT name, veikkaus, veto_id, tapahtuma_id FROM tapahtumaveto"
                     " WHERE tapahtumaveto.veto_id = :id"
                     ).params(id=row[0]) #veto.id
            res2 = db.engine.execute(stmt2)
            ratkeaa = datetime.now()-timedelta(minutes = 60)
            nimi = ""
            for row2 in res2:
                nimi = row2[0]
                stmt3 = text("SELECT koti, vieras, tulos, date_expire, active FROM tapahtuma"
                     " WHERE tapahtuma.id = :id"
                     ).params(id=row2[3]) #tapahtumaveto.tapahtuma_id
                res3 = db.engine.execute(stmt3)
                
                for data in res3:
                    row3 = data
                if (len(row3) > 4):
                    if (str(row3[4]) == "False"):
                        non_actives = True
                        active = 0
                    else:
                        actives = True
                    new_ratkeaa = datetime.strptime(str(row3[3]), '%Y-%m-%d %H:%M:%S.%f')
                    if new_ratkeaa > ratkeaa:
                        ratkeaa = new_ratkeaa
                    if(actives == True and non_actives == True):
                        active=2
                vedot.append({"veikkaus":row2[1], "koti":row3[0], "vieras":row3[1], "tulos":row3[2]})
    
            
            if (ratkeaa < datetime.now()):
                
                if (row3[2] == "kesken"):
                    ratkeaa = "kesken"
                else:
                    ratkeaa = "ratkennut"
                  
                    if (int(row[3]) > 0):
                        ratkeaa += ", voitto: "
                        ratkeaa += str(row[3])
                    else:
                        ratkeaa += ", ei voittoa"
            else :
                ratkeaa = str(str(ratkeaa)[0:16])
                
            response.append({"id":row[0], "nimi": nimi, "tapahtumavedot": vedot, "panos":row[1] , "kerroin":kerroin, "ratkeaa":ratkeaa, "active":active})   
  
        return response
    
    @staticmethod
    def find_veto_byId(user_id, veto_id):
        stmt = text("SELECT id, panos, kerroin, voitto FROM veto"
                     " WHERE veto.account_id = :user_id"
                     " AND veto.id = :veto_id"
                     ).params(user_id=user_id, veto_id=veto_id)
        res = db.engine.execute(stmt)

        response = []
        for row in res:
            vedot = []
            row3 = []
            active = 0
            stmt2 = text("SELECT name, veikkaus, veto_id, tapahtuma_id FROM tapahtumaveto"
                     " WHERE tapahtumaveto.veto_id = :id"
                     ).params(id=row[0]) #veto.id
            res2 = db.engine.execute(stmt2)
            
            nimi = ""
            for row2 in res2:
                nimi = row2[0]
                stmt3 = text("SELECT koti, vieras, tulos, date_expire, active FROM tapahtuma"
                     " WHERE tapahtuma.id = :id"
                     ).params(id=row2[3]) #tapahtumaveto.tapahtuma_id
                res3 = db.engine.execute(stmt3)
                
                for data in res3:
                    row3 = data
                if (len(row3) > 4):
                    if (str(row3[4]) == "1"):
                        active = 1  
                    
                vedot.append({"veikkaus":row2[1], "koti":row3[0], "vieras":row3[1], "tulos":row3[2]})

            ratkeaa = "kesken"    
            response.append({"id":row[0], "nimi": nimi, "tapahtumavedot": vedot, "panos":row[1] , "kerroin":row[2] , "ratkeaa":ratkeaa, "active":active})   
            
        return response
    
    
