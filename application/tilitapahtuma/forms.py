from flask_wtf import FlaskForm
from wtforms import IntegerField, validators

class TilisiirtoForm(FlaskForm):
    tilisiirto = IntegerField("Summa", [validators.NumberRange(min = 0, max = 10000, message="Anna positiivinen luku")])
    
    class Meta:
        csrf = False


class PankkisiirtoForm(FlaskForm):
    pankkisiirto = IntegerField("Summa", [validators.NumberRange(min = 0, max = 10000, message="Anna positiivinen luku")])
    
    class Meta:
        csrf = False