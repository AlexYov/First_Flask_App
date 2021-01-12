from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from app import application, db


@application.route('/', methods = ['GET','POST'])
@login_required
def index():
    
    title = 'Homepage'
    users = User.query.all()
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body = form.post.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash('Пост опубликован')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type = int)
    posts = current_user.followed_posts().paginate(page, application.config['POSTS_PER_PAGE'], False)
    next_page = None
    prev_page = None
    if posts.has_next:
        next_page = url_for('index', page = posts.next_num)
    if posts.has_prev:
        prev_page = url_for('index', page = posts.prev_num)
    return render_template('index.html', title = title, users = users, posts = posts.items, form = form, next_page = next_page, prev_page = prev_page)


@application.route('/login', methods = ['GET', 'POST'])
def login():
    
    title = 'Login'
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Не верный логин или пароль')
            return redirect(url_for('login'))
        login_user(user, remember = form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', form = form, title = title)


@application.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@application.route('/signin', methods = ['GET', 'POST'])
def signin():
    
    title = 'Sign in'
    if current_user.is_authenticated:
        redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.email_validate() or form.username_validate():
            pass
        else:
            user = User(username = form.username.data, email = form.email.data)
            user.set_password(form.password_first.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('signin.html', title = title, form = form)


@application.route('/user/<user_name>')
@login_required
def user_auth(user_name):
    user = User.query.filter_by(username = user_name).first_or_404()
    page = request.args.get('page', 1, type = int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, application.config['POSTS_PER_PAGE'], False)
    next_page = None
    prev_page = None
    if posts.has_next:
        next_page = url_for('user_auth', page = posts.next_num, user_name = user.username)
    if posts.has_prev:
        prev_page = url_for('user_auth', page = posts.prev_num, user_name = user.username)
    return render_template('user.html', user = user, posts = posts.items, next_page = next_page, prev_page = prev_page)


@application.route('/edit_profile', methods = ['GET','POST'])
@login_required
def edit_user_profile():
    
    form = EditProfileForm()
    title = 'Edit profile'
    if form.validate_on_submit():
        if form.email_validate() or form.username_validate() or form.old_password_validate() != True:
            pass
        else:
            current_user.set_password(form.new_password.data)
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Данные успешно сохранены!')
            return redirect(url_for('edit_user_profile'))
    return render_template('user_profile.html', form = form, title = title)
    
    
@application.route('/follow/<another_username>')
@login_required
def follow(another_username):
    
    user = User.query.filter_by(username = another_username).first()
    if user is None:
        flash(f'Пользователь {another_username} не найден')
        return redirect(url_for('index'))
    elif user == current_user:
        flash('Вы не можете подписаться на самого себя')
        return redirect(url_for('user_auth', user_name = user))
    else:
        current_user.follow(user)
        db.session.commit()
        flash(f'Вы подписались на пользователя {user.username}')
    return redirect(url_for('user_auth', user_name = user.username))


@application.route('/unfollow/<another_username>')
@login_required
def unfollow(another_username):
    
    user = User.query.filter_by(username = another_username).first()
    if user is None:
        flash(f'Пользователь {another_username} не найден')
        return redirect(url_for('index'))
    elif user == current_user:
        flash('Вы не можете отписаться от самого себя')
        return redirect(url_for('user_auth', user_name = user))
    else:
        current_user.unfollow(user)
        db.session.commit()
        flash(f'Вы отписались от пользователя {user.username}')
    return redirect(url_for('user_auth', user_name = user.username))


@application.route('/explorer')
@login_required
def explorer():
    
    title = 'Explorer'
    page = request.args.get('page', 1, type = int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, application.config['POSTS_PER_PAGE'], False)
    next_page = None
    prev_page = None
    if posts.has_next:
        next_page = url_for('explorer', page = posts.next_num)
    if posts.has_prev:
        prev_page = url_for('explorer', page = posts.prev_num)  
    return render_template('index.html', title = title, posts = posts.items, next_page = next_page, prev_page = prev_page)