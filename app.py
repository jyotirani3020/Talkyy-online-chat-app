from flask import Flask, render_template,request, redirect, url_for, flash
from forms import *
from models import *
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256
from flask_login import logout_user,login_required, LoginManager, login_user,current_user
from flask_socketio import SocketIO,send,emit,join_room,leave_room
from time import localtime,strftime

app = Flask(__name__)
#app.secret_key = os.environ.get('SECRET')
app.secret_key = 'test'
socketio = SocketIO(app)
ROOMS = ["lounge","news", "games", "coding"]

app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://klwcwdosiorkjf:06248ef89077295ce6ce6c7aeaf41c7a196631c4b5e7a689f2dc55ed8ae5f4e7@ec2-23-22-156-110.compute-1.amazonaws.com:5432/d7ffpoa9ipvup1"
db = SQLAlchemy(app)
login = LoginManager(app)
login.init_app(app)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/', methods=["GET", "POST"])
def index():
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data
        hashed_password = pbkdf2_sha256.hash(password)

        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('registered successfully, please login','success')
        return redirect(url_for('login'))
    return render_template("index.html", form=reg_form)

@app.route('/login', methods=['POST','GET'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user_object = User.query.filter_by(username=login_form.username.data).first()
        login_user(user_object)
        return redirect(url_for('chat'))
  

    return render_template("login.html",form=login_form)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if not current_user.is_authenticated:
        flash('please login','danger')
        return redirect(url_for('login'))

    return render_template('chat.html', username=current_user.username, rooms=ROOMS)

@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    flash('You are logged out successfully', 'success')
    return redirect(url_for('login')) 

@socketio.on('incoming-msg')
def message(data):
    print(f"\n\n{data}\n\n")
    send({'msg': data['msg'], 'username': data['username'], 'time_stamp': strftime("%b-%d %I:%M%p", localtime())}, room=data['room'])

@socketio.on('join')
def join(data):
    join_room(data['room'])
    send({'msg': data['username']+ " has joined the " + data['room'] + "room."}, room=data['room'])

@socketio.on('leave')
def leave(data):
    leave_room(data['room'])
    send({'msg': data['username']+ " has left the " + data['room'] + "room."}, room=data['room'])


if __name__ == '__main__':
    socketio.run(app, debug=True)