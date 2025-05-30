from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo


class RegisterForm(FlaskForm):
    login = StringField("Логин", validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired()])
    about = TextAreaField("О себе")
    avatar = FileField("Аватар", validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')])
    password = PasswordField("Пароль", validators=[DataRequired()])
    password_again = PasswordField("Повторите пароль", validators=[DataRequired(), EqualTo('password', message="Пароли должны совпадать")])
    submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
    login = StringField("Логин", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")