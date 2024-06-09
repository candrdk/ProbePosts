from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

from urllib.parse import urlsplit
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import date

from app import app, pgdb
from app.forms import LoginForm, RegistrationForm, CreatePostForm, CreateSearchForm
from app.models import User, Post


@app.context_processor
def inject_search_form():
    return dict(searchform=CreateSearchForm())

@app.before_request
def handle_searchform_submission():
    if request.method == 'POST' and 'search' in request.form:
        form_data = request.form['search']
        # Redirect to a specific route or handle as needed
        return redirect(url_for('search') + f'?q={form_data}')


@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('feed.html', title="Home")
    else:
        return redirect(url_for('login'))

@app.route('/page/<int:page_num>', methods=['GET'])
@login_required
@pgdb.connect
def home_page(db, page_num):
    posts_data = db.query_recent_posts_page(10, page_num)
    posts = [Post(db, p, current_user.id) for p in posts_data]
    return render_template('page.html', posts=posts)

@app.route('/following')
@login_required
@pgdb.connect
def following(db):
    return render_template('feed.html', title='Following')

@app.route('/following/page/<int:page_num>', methods=['GET'])
@login_required
@pgdb.connect
def following_page(db, page_num):
    posts_data = db.query_recent_following_posts_page(current_user.id, 10, page_num)
    posts = [Post(db, p, current_user.id) for p in posts_data]
    return render_template('page.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
@pgdb.connect
def login(db):
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
@login_required
@pgdb.connect
def logout(db):
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
@pgdb.connect
def register(db):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        db.insert_user(User({
            'handle': form.handle.data,
            'display_name': form.handle.data,
            'password_hash': generate_password_hash(form.password.data),
            'state_code': None if form.state.data == '' else form.state.data,
            'city_id':  None if form.city_id == '' else form.city_id
        }))

        flash('You are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', cities=db.query_cities(), form=form)

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
@pgdb.connect
def create_post(db):
    form = CreatePostForm()
    
    if form.validate_on_submit():
        p = Post(db, {
            'poster_id': current_user.id,
            'post_date': date.today(),
            'sighting_date': form.sightingDateTime.data.date(),
            'sighting_time': form.sightingDateTime.data.time(),
            'state_code': None if form.state.data == '' else form.state.data,
            'city_id': form.city_id,
            'summary': form.summary.data, 
            'duration': form.sightingDuration.data,
            'image_url': form.imageUrl.data,
            'latitude': form.latField.data,
            'longitude': form.lonField.data
        })

        db.insert_post(p)
        return redirect(url_for('index'))

    return render_template('create_post.html', title='Create Post', cities=db.query_cities(), form=form)


@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q')
    return render_template('feed.html', title="Search", searchvalue=query)

@app.route('/search/page/<int:page_num>', methods=['GET'])
@login_required
@pgdb.connect
def search_page(db, page_num):
    query = request.args.get('q')
    posts_data = db.query_search_posts_page(query, 10, page_num)
    posts = [Post(db, p, current_user.id) for p in posts_data]
    return render_template('page.html', posts=posts)

@app.route('/@<handle>')
@login_required
@pgdb.connect
def profile(db, handle):
    user_data = db.query_userdata_by_handle(handle)
    if user_data is None:
        flash(f'No user exists with handle @{handle}')
        return redirect(url_for('index'))
    
    user = User(user_data)

    return render_template('profile.html', title="Profile", user=user.get_profile_data(current_user.id))

@app.route('/@<handle>/follow', methods=['GET'])
@login_required
@pgdb.connect
def follow(db, handle):
    db.insert_follow(current_user.id, db.query_user_id(handle))
    return 'followed'

@app.route('/@<handle>/unfollow', methods=['GET'])
@login_required
@pgdb.connect
def unfollow(db, handle):
    db.delete_follow(current_user.id, db.query_user_id(handle))
    return 'unfollowed'

@app.route('/@<handle>/likes', methods=['GET'])
@login_required
@pgdb.connect
def user_likes(db, handle):
    user_data = db.query_userdata_by_handle(handle)
    if user_data is None:
        flash(f'No user exists with handle @{handle}')
        return redirect(url_for('index'))
    
    user = User(user_data)

    return render_template('profile.html', title="Profile", user=user.get_profile_data(current_user.id))

@app.route('/@<handle>/likes/page/<int:page_num>', methods=['GET'])
@login_required
@pgdb.connect
def user_likes_page(db, handle, page_num):
    user_id = db.query_user_id(handle)
    posts_data = db.query_user_liked_posts_page(user_id, 10, page_num)
    posts = [Post(db, p, current_user.id) for p in posts_data]
    return render_template('page.html', posts=posts)


@app.route('/@<handle>/page/<int:page_num>', methods=['GET'])
@login_required
@pgdb.connect
def user_page(db, handle, page_num):
    user_id = db.query_user_id(handle)
    posts_data = db.query_recent_posts_by_user_page(user_id, 10, page_num)
    posts = [Post(db, p, current_user.id) for p in posts_data]
    return render_template('page.html', posts=posts)

@app.route('/<vote_type>/<post_id>', methods=['GET'])
@login_required
@pgdb.connect
def upvote(db, vote_type, post_id):
    if vote_type == 'upvote':
        db.query_rate_post(current_user.id, post_id, True)
    elif vote_type == 'downvote':
        db.query_rate_post(current_user.id, post_id, False)

    karma = db.query_post_karma(post_id)
    rating = db.query_post_rating(current_user.id, post_id)
    return render_template('post_rating.html', post_id=post_id, karma=karma, rating=rating)
