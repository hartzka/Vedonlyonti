from application import db
from application.models import Base

class Laji(Base):
    
    nimi = db.Column(db.String, nullable=False)
    
    def __init__(self, nimi):
        self.nimi = nimi