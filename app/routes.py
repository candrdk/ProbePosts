from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required

from urllib.parse import urlsplit
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db
from app.forms import LoginForm, RegistrationForm, CreatePostForm, CreateSearchForm
from app.models import User, Post
from datetime import date

@app.route('/')
@app.route('/index')
@login_required
def index():
    posts_data = db.query_recent_posts(100)
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

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = CreatePostForm()
    
    if form.validate_on_submit():
        p = Post({
            'poster_id': current_user.id,
            'post_date': date.today(),
            'sighting_date': form.sightingDateTime.data.date(),
            'sighting_time': form.sightingDateTime.data.time(),
            'state_code': None if form.state.data == '' else form.state.data,
            'city_id':  None if form.city.data == '' else form.city.data,
            'summary': form.summary.data, 
            'duration': form.sightingDuration.data,
            'image_url': form.imageUrl.data,
            'latitude': form.latField.data,
            'longitude': form.lonField.data
        })
        db.insert_post(p)
        return redirect(url_for('index'))
    return render_template('create_post.html', title='Create Post', form=form)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = CreateSearchForm()

    # TODO: USE FORM
    
    posts_data = db.query_recent_posts(3)
    posts = [Post(p) for p in posts_data]

    return render_template('search.html', title="Search", form=form, posts=posts)

@app.route('/@<handle>')
def profile(handle):

    user_data = db.query_userdata_by_handle(handle)
    if user_data is None:
        flash(f'No user exists with handle @{handle}')
        return redirect(url_for(f'/@{handle}'))
    
    user = User(user_data)

    profile_data = {
        "displayname":user.display_name,
        "handle":user.handle,
        "state":db.query_state_name(user.state_code),
        "city":db.query_city_name(user.city_id)
    }

    print(user.user_id)

    posts_data = db.query_posts_by_user_id(user.user_id)
    posts = [Post(p) for p in posts_data]

    print(len(posts))

    # TODO: load profile data from url
    # TODO: display all users posts underneath

    return render_template('profile.html', title="Profile", user=profile_data, posts=posts)


@app.route('/upvote/<post_id>', methods=['POST'])
def upvote(post_id):
    print('up', post_id)
    return jsonify({'type': 'upvote', 'post_id':post_id})


@app.route('/downvote/<post_id>', methods=['POST'])
def downvote(post_id):
    print('down', post_id)
    return jsonify({'type': 'downvote', 'post_id':post_id})