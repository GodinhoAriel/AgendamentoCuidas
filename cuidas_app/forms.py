from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class AgendamentoForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(min=10)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = IntegerField('Telefone', validators=[DataRequired()])
    submit = SubmitField('Próximo')