from flask import Flask, render_template, redirect, request, abort
from data import db_session
from data.users import User
from data.messages import Message
from data.notes import Note
from forms.account import RegisterForm, LoginForm
from forms.note_editor import ChatForm, NoteForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
import resources
from ai import messages_context, generate
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['SECRET_KEY'] = "sample_key"
login_manager = LoginManager()
login_manager.init_app(app)

api = Api(app)
api.add_resource(resources.NoteListResource, '/api/notes')
api.add_resource(resources.NoteResource, '/api/notes/<int:note_id>')
api.add_resource(resources.MessageListResource, '/api/messages')
api.add_resource(resources.MessageResource, '/api/messages/<int:message_id>')


def main():
    db_session.global_init("db/psychology.db")
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect("/dashboard")
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template("register.html", title="Регистрация",
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.login == form.login.data).first():
            return render_template("register.html", title="Регистрация",
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            login=form.login.data,
            name=form.name.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        if form.avatar.data:
            filename = secure_filename(form.login.data + '.jpg')
            form.avatar.data.save(os.path.join('static/img', filename))
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                            message="Неправильный логин или пароль",
                            form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/dashboard")
@login_required
def dashboard():
    db_sess = db_session.create_session()
    all_notes = db_sess.query(Note).filter(Note.user == current_user).limit(5)
    all_messages = db_sess.query(Message).filter(Message.user == current_user).limit(5)
    hist = db_sess.query(Message).filter(Message.user_id == current_user.id)
    ctx = messages_context(hist, "ПРЕДЛОЖИ ПСИХОЛОГИЧЕСКИЕ ТЕСТЫ | ")
    tests = generate(ctx).strip().replace(" ", "_").split("\n")
    return render_template("dashboard.html", notes=all_notes, messages=all_messages, tests=tests, title="Панель управления")


@app.route("/chat", methods=['GET', 'POST'])
@login_required
def chat():
    db_sess = db_session.create_session()
    all_messages = db_sess.query(Message).filter(Message.user == current_user)
    form = ChatForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        message = Message()
        message.question = "СООБЩЕНИЕ ОТ ПОЛЬЗОВАТЕЛЯ | " + form.text.data
        hist = db_sess.query(Message).filter(Message.user_id == current_user.id)
        ctx = messages_context(hist, "СООБЩЕНИЕ ОТ ПОЛЬЗОВАТЕЛЯ | " + form.text.data)
        message.answer = generate(ctx)
        user = db_sess.query(User).get(current_user.id)
        user.messages.append(message)
        db_sess.commit()
        return redirect("/chat")
    return render_template("chat.html", messages=all_messages, form=form, title="Чат")


@app.route("/new_note", methods=['GET', 'POST'])
@login_required
def new_note():
    form = NoteForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        note = Note()
        note.mood = int(form.mood.data)
        note.comment = form.text.data
        message = Message()
        message.question = "ЗАПИСЬ О НАСТРОЕНИИ | " + form.text.data
        hist = db_sess.query(Message).filter(Message.user_id == current_user.id)
        ctx = messages_context(hist, "ЗАПИСЬ О НАСТРОЕНИИ | " + str(form.mood.data) + "/5 - " + form.text.data)
        message.answer = generate(ctx)
        user = db_sess.query(User).get(current_user.id)
        user.notes.append(note)
        user.messages.append(message)
        db_sess.commit()
        return redirect("/")
    return render_template("new_note.html", title="Новая запись", form=form)


@app.route("/edit_note/<int:note_id>", methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    db_sess = db_session.create_session()
    note = db_sess.query(Note).filter(Note.id == note_id, Note.user == current_user).first()
    if not note:
        abort(404)
    
    form = NoteForm()
    if form.validate_on_submit():
        # Повторная проверка существования записи перед сохранением
        note = db_sess.query(Note).filter(Note.id == note_id, Note.user == current_user).first()
        if not note:
            abort(404)

        note.mood = int(form.mood.data)
        note.comment = form.text.data
        db_sess.commit()
        return redirect("/")
    
    if request.method == "GET":
        form.mood.data = str(note.mood)
        form.text.data = note.comment
    
    return render_template("edit_note.html", title="Редактировать запись", form=form)


# ИИ сам генерирует вопросы на основе заголовка из адреса, а в шаблоне они расставляются по местам
@app.route("/psychological_test/<name>", methods=['GET', 'POST'])
@login_required
def psychological_test(name):
    db_sess = db_session.create_session()
    if request.method == "POST":
        answers = []
        for i in range(1, 6):
            answer = request.form.get(f'answer{i}')
            if answer:
                answers.append(answer)
        results_message = f"РЕЗУЛЬТАТЫ ТЕСТА | {name}\n" + "\n".join(answers)
        hist = db_sess.query(Message).filter(Message.user_id == current_user.id)
        ctx = messages_context(hist, results_message)
        message = Message(
            question=results_message,
            answer=generate(ctx),
            user_id=current_user.id
        )
        db_sess.add(message)
        db_sess.commit()
        return redirect("/")
    hist = db_sess.query(Message).filter(Message.user_id == current_user.id)
    ctx = messages_context(hist, "НОВЫЙ ПСИХОЛОГИЧЕСКИЙ ТЕСТ | " + name)
    survey = generate(ctx).strip().split("\n")
    return render_template("psychological_test.html", survey=survey, title="Психологический тест", name=name)
    

if __name__ == '__main__':
    main()
