from app import db, login, application
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
import jwt

'''Модель базы данных'''

# таблица followers находится за пределами класса User, но данный класс может обращаться к таблице followers благодаря внешним ключам в этой таблице, которые ссылаются на класс User: 'user.id' 
followers = db.Table('followers', db.Column('follower_id', db.Integer, db.ForeignKey('user.id')), db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))) 

# класс, отвечающий за учётные записи пользователей, а также за их функционал
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True) #это уникальный идентификатор пользователя
    username = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    followed = db.relationship('User', secondary = followers, primaryjoin = (followers.c.follower_id == id), secondaryjoin = (followers.c.followed_id == id), backref = db.backref('followers', lazy = 'dynamic'), lazy = 'dynamic') 

    def followed_posts(self):
        followed = Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id = self.id)
        return followed.union(own).order_by(Post.timestamp.desc())
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    #Генерируем хэш-пароля
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    #Сравниваем хэш с паролем, который предоставил пользователь
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)  
    
    # получаем токен безопасности для сброса пароля
    def get_reset_password_token(self, time_token = 600):
        return jwt.encode({'user_id' : self.id, 'finish_token' : time() + time_token}, application.config['SECRET_KEY'], algorithm = 'HS256')
    
    # проверка полученного токена
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, application.config['SERCRET_KEY'], algorithms=['HS256'])['user_id']
        except:
            return None
        return User.query.get(id)
    
# класс, отвечающий за посты/сообщения пользователей        
class Post(db.Model):
    id_post = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
'''Конец модели'''

@login.user_loader
def load_user(id): #функция user_loader принимает id (уникальный идентификатор авторизованного пользователя). переменная, содержащая уникальный идентификатор пользователя, должна называться id, не user_id или id_user, а именно id, иначе выйдет ошибка "NotImplementedError: No `id` attribute - override `get_id`"
    return User.query.get(int(id))