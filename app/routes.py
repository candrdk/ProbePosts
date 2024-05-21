from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

from urllib.parse import urlsplit
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User, Post

@app.route('/')
@app.route('/index')
@login_required
def index():
    posts_data = db.query_recent_posts(3)
    posts = [Post(p) for p in posts_data]

    return render_template('index.html', title="Home", posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user_data = db.query_userdata_by_handle(form.handle.data)

        if user_data is None or not check_password_hash(user_data['password_hash'], form.password.data):
            flash('Invalid handle or password')
            return redirect(url_for('login'))
        
        user = User(user_data)
        
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
        db.insert_user(User({
            'handle': form.handle.data,
            'display_name': form.handle.data,
            'password_hash': generate_password_hash(form.password.data),
            'state_code': None if form.state.data == '' else form.state.data,
            'city_id':  None if form.city.data  == '' else form.city.data
        }))

        flash('You are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)
