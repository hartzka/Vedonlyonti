from flask_wtf import FlaskForm
from wtforms import SelectField

ChoicesMoniveto = [('-', '-'), ('1', '1'), ('X', 'X'), ('2', '2')]
ChoicesTulosveto = [('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10+', '10+')]

class TapahtumaForm(FlaskForm):
    moniveto1 = SelectField('Veikkaus', choices=ChoicesMoniveto)
    moniveto2 = SelectField('Veikkaus', choices=ChoicesMoniveto)
    moniveto3 = SelectField('Veikkaus', choices=ChoicesMoniveto)

    tulosveto_koti = SelectField('Veikkaus', choices=ChoicesTulosveto)
    tulosveto_vieras = SelectField('Veikkaus', choices=ChoicesTulosveto)
    
    panos = SelectField('Panos', choices=[('1','1.00'), ('2','2.00'), ('3','3.00'), ('5','5.00'), ('10','10.00'), ('20','20.00')])
 
    class Meta:
        csrf = False