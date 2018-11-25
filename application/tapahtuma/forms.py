from flask_wtf import FlaskForm
from wtforms import SelectField

Choices = [('-', '-'), ('1', '1'), ('X', 'X'), ('2', '2')]

class TapahtumaForm(FlaskForm):
    veto1 = SelectField('Veikkaus', choices=Choices)
    veto2 = SelectField('Veikkaus', choices=Choices)
    veto3 = SelectField('Veikkaus', choices=Choices)

    panos = SelectField('Panos', choices=[('1','1.00'), ('2','2.00'), ('3','3.00'), ('5','5.00'), ('10','10.00'), ('20','20.00')])
 
    class Meta:
        csrf = False