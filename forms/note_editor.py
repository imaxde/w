from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, IntegerField, HiddenField
from wtforms.validators import DataRequired, NumberRange


class ChatForm(FlaskForm):
    text = TextAreaField("Введите сообщение", validators=[DataRequired()])
    submit = SubmitField("Отправить")


class NoteForm(FlaskForm):
    mood = IntegerField("Настроение", validators=[DataRequired(), NumberRange(min=1, max=5)])
    text = TextAreaField("Опишите ваше состояние", validators=[DataRequired()])
    submit = SubmitField("Сохранить")
