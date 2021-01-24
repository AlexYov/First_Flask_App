from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from werkzeug.urls import url_parse
from app.auth.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, StartResetPasswordForm, FinishResetPasswordForm
from app import db
from app.auth.email import send_email
from app.auth import bp


@bp.route('/', methods = ['GET','POST'])
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
        return redirect(url_for('auth.index'))
    page = request.args.get('page', 1, type = int)
    posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_page = None
    prev_page = None
    if posts.has_next:
        next_page = url_for('auth.index', page = posts.next_num)
    if posts.has_prev:
        prev_page = url_for('auth.index', page = posts.prev_num)
    return render_template('index.html', title = title, users = users, posts = posts.items, form = form, next_page = next_page, prev_page = prev_page)


@bp.route('/login', methods = ['GET', 'POST'])
def login():
    
    title = 'Login'
    
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Не верный логин или пароль')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember = form.remember_me.data)
        
        next_page = request.args.get('next')
        
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('auth.index')
            
        return redirect(next_page)
    
    return render_template('auth/login.html', form = form, title = title)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.index'))


@bp.route('/signin', methods = ['GET', 'POST'])
def signin():
    
    title = 'Sign in'
    
    if current_user.is_authenticated:
        redirect(url_for('auth.index'))
        
    form = RegistrationForm()
    
    if form.validate_on_submit():
        if form.email_validate() or form.username_validate():
            pass
        else:
            user = User(username = form.username.data, email = form.email.data)
            user.set_password(form.password_first.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('auth.login'))
    return render_template('auth/signin.html', title = title, form = form)


@bp.route('/user/<user_name>')
@login_required
def user_auth(user_name):
    user = User.query.filter_by(username = user_name).first_or_404()
    page = request.args.get('page', 1, type = int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_page = None
    prev_page = None
    if posts.has_next:
        next_page = url_for('auth.user_auth', page = posts.next_num, user_name = user.username)
    if posts.has_prev:
        prev_page = url_for('auth.user_auth', page = posts.prev_num, user_name = user.username)
    return render_template('user.html', user = user, posts = posts.items, next_page = next_page, prev_page = prev_page)


@bp.route('/edit_profile', methods = ['GET','POST'])
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
            return redirect(url_for('auth.edit_user_profile'))
    return render_template('user_profile.html', form = form, title = title)
    
    
@bp.route('/follow/<another_username>')
@login_required
def follow(another_username):
    
    user = User.query.filter_by(username = another_username).first()
    if user is None:
        flash(f'Пользователь {another_username} не найден')
        return redirect(url_for('auth.index'))
    elif user == current_user:
        flash('Вы не можете подписаться на самого себя')
        return redirect(url_for('auth.user_auth', user_name = user))
    else:
        current_user.follow(user)
        db.session.commit()
        flash(f'Вы подписались на пользователя {user.username}')
    return redirect(url_for('auth.user_auth', user_name = user.username))


@bp.route('/unfollow/<another_username>')
@login_required
def unfollow(another_username):
    
    user = User.query.filter_by(username = another_username).first()
    if user is None:
        flash(f'Пользователь {another_username} не найден')
        return redirect(url_for('auth.index'))
    elif user == current_user:
        flash('Вы не можете отписаться от самого себя')
        return redirect(url_for('auth.user_auth', user_name = user))
    else:
        current_user.unfollow(user)
        db.session.commit()
        flash(f'Вы отписались от пользователя {user.username}')
    return redirect(url_for('auth.user_auth', user_name = user.username))


@bp.route('/explorer')
@login_required
def explorer():
    
    title = 'Explorer'
    
    page = request.args.get('page', 1, type = int)
    
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    
    next_page = None
    
    prev_page = None
    
    if posts.has_next:
        next_page = url_for('auth.explorer', page = posts.next_num)
        
    if posts.has_prev:
        prev_page = url_for('auth.explorer', page = posts.prev_num)  
        
    return render_template('index.html', title = title, posts = posts.items, next_page = next_page, prev_page = prev_page)


@bp.route('/reset_password', methods = ['GET', 'POST'])
def reset_password_request():

    title = 'Reset password'
    
    if current_user.is_authenticated:
        redirect(url_for('auth.index')) 
        
    form = StartResetPasswordForm()
    
    if form.validate_on_submit():
        
        if form.email_validate():
            pass
        
        else:
            user = User.query.filter_by(email = form.email.data).first()
            token = user.get_reset_password_token()
            html_body = render_template('auth/reset_password.html', user = user, token = token)
            send_email(subject = 'Сброс пароля', sender = 'info@reset.pass', recipients = [user.email], html_body = html_body)
            flash(f'Вам отправлено письмо на почту {user.email}')
            return redirect(url_for('auth.reset_password_request'))
        
    return render_template('auth/start_reset_password_form.html', form = form, title = title)


@bp.route('/reset_password/<token>', methods = ['GET', 'POST'])
def reset_password_token(token):
    
    title = 'Reset password'
    
    if current_user.is_authenticated:
        redirect(url_for('auth.index'))
        
    user_verify = User.verify_reset_password_token(token)

    form = FinishResetPasswordForm()
    
    if form.validate_on_submit():
        if user_verify == None:
            redirect(url_for('auth.index'))
        else:
            user_verify.set_password(form.first_password.data)
            db.session.commit()
            flash('Пароль изменён')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/finish_reset_password_form.html', form = form, title = title)