from flask import Flask, render_template, redirect, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from werkzeug.utils import secure_filename
from datetime import datetime, date
import os

app = Flask(__name__)
app.config.update(
    SECRET_KEY="secret",
    SQLALCHEMY_DATABASE_URI="sqlite:///page.db",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    UPLOAD_FOLDER='static/images',
    MAX_CONTENT_LENGTH=2 * 1024 * 1024
)

db = SQLAlchemy(app)

class Base(DeclarativeBase): pass

class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(100))
    birthdate: Mapped[str] = mapped_column(String(100))
    profile_pic: Mapped[str] = mapped_column(String(200), nullable=True)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form['username'], 
            password=request.form['password']
        ).first()

        if user:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        return render_template("login.html", error="Invalid username or password.")

    return render_template("login.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        if User.query.filter_by(username=username).first():
            return render_template("signup.html", error="Username already exists.")

        profile_pic = request.files.get('profile_pic')
        filename = secure_filename(profile_pic.filename) if profile_pic and profile_pic.filename else None
        if filename:
            profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_user = User(
            name=request.form['name'],
            birthdate=request.form['birthdate'],
            address=request.form['address'],
            username=username,
            password=request.form['password'],
            profile_pic=filename
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template("signup.html")

@app.route('/home')
def home():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    birthdate = datetime.strptime(user.birthdate, "%Y-%m-%d").date()
    age = date.today().year - birthdate.year - ((date.today().month, date.today().day) < (birthdate.month, birthdate.day))
    return render_template('home.html', user=user, age=age)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
