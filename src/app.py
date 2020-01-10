import os

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash


from helpers import login_required
from models import db, User, ShortUrl

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "my-secret-key"
db.init_app(app)

def main():
    db.create_all()

@app.route("/")
def land_page():
    return render_template('index.html')

@app.route("/home")
@login_required
def home():
    user = User.query.filter_by(username=session['username']).first()
    print(user)
    return render_template('home.html', user=user)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            password1 = request.form.get('password1')
            user = User.query.filter_by(username=username).first()
            if user is not None:
                flash('Username already exist')
                return redirect(url_for('register'))
            if password != password1:
                flash('Passwords do not match')
                return redirect(url_for('register'))
            pwd = generate_password_hash(password)
            new_user = User(username=username,password=pwd)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = new_user.username
            flash('You successfuly created an acount')
            return redirect(url_for('login'))
        except HTTPException as e:
            flash(e)
            return e

    if request.method == 'GET':
        return render_template('register.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'POST':
        try:
            user = User.query.filter_by(username=request.form.get('username')).first()
            if user is None:
                flash("Wrong username")
                return redirect(url_for('login'))
            if not check_password_hash(user.password, request.form.get('password')):
                flash("Wrong password")
                return redirect(url_for('login'))
            user.authenticated = True
            session['username'] = user.username
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('home'))
        except HTTPException as e:
            flash(e)
            return e
    else:
        return render_template('login.html')

@app.route("/logout")
def logout():
    user = User.query.filter_by(username=session['username']).first()
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    session.clear()
    return redirect(url_for('land_page'))

@app.route("/terms")
def terms():
    return render_template('licence.html')


if __name__ == "__main__":
    with app.app_context():
        main()