from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

from urllib.parse import urlsplit
from werkzeug.security import generate_password_hash, check_password_hash

from app import app
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app.queries import get_user_by_username, insert_user

@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'Alice'},
            'body': 'Sample post 1.'
        },
        {
            'author': {'username': 'Bob'},
            'body': 'Sample post 2.'
        }
    ]

    return render_template('index.html', title="Home", posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = get_user_by_username(form.username.data)

        if user is None or not check_password_hash(user.password_hash, form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)

    return render_template('login.html', title="Sign In", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        insert_user(User({
            'username': form.username.data,
            'password_hash': generate_password_hash(form.password.data),
            'country': 'United States'
        }))

        flash('You are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)
