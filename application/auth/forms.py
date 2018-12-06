from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, validators
  
class LoginForm(FlaskForm):
    tunnus = StringField("Käyttäjätunnus", [validators.Length(min=2)])
    nimi = StringField("Nimi",[validators.Length(min=2)])
    salasana = PasswordField("Salasana",[validators.Length(min=2)])
  
    class Meta:
        csrf = False