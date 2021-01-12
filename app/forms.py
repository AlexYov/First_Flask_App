from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Length
from email_validator import validate_email, EmailNotValidError
from app.models import User
from flask_login import current_user

class LoginForm(FlaskForm):
    
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Вход')
    
class RegistrationForm(FlaskForm):
    
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired()])
    password_first = PasswordField('Пароль', validators=[DataRequired()])
    password_repeat = PasswordField('Повторить пароль', validators=[DataRequired(), EqualTo('password_first')])
    submit = SubmitField('Зарегистрироваться')

    def username_validate(self,):
        user_username = User.query.filter_by(username = self.username.data).first()
        if user_username is not None:
            return ValidationError('Этот логин занят')
        
    def email_validate(self,):
        try:
            validate_email(self.email.data)
        except EmailNotValidError:
            return ValidationError('Некорректная почта')
        except:
            pass        
        
class EditProfileForm(FlaskForm):
    
    username = StringField('Имя пользователя', validators=[DataRequired()])
    old_password = PasswordField('Старый пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
    
    def old_password_validate(self):
        try:
            if current_user.check_password(self.old_password.data) == True:
                return True
        except TypeError:
            pass
        except:
            return ValidationError('Не верный пароль')
    
    def username_validate(self):
        user_username = User.query.filter_by(username = self.username.data).first()
        if user_username is not None:
            return ValidationError('Этот логин занят')
        
    def email_validate(self):
        try:
            validate_email(self.email.data)
        except EmailNotValidError:
            return ValidationError('Некорректная почта')
        except:
            pass
        
class PostForm(FlaskForm):
    post = TextAreaField('Текст:', validators = [DataRequired(), Length(min = 1, max = 140)])
    submit = SubmitField('Отправить')