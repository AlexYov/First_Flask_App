from flask import Flask
from config_file import BaseConfig
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import logging
from logging.handlers import SMTPHandler


db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()

def create_app(config_class = BaseConfig):
    
    application = Flask(__name__)
    application.config.from_object(config_class) 
    
    db.init_app(application)
    login.init_app(application)
    mail.init_app(application)  

    from app.errors import bp as errors_bp
    application.register_blueprint(errors_bp)
    
    from app.auth import bp as auth_bp
    application.register_blueprint(auth_bp, url_prefix = '/auth')
    
    
    if not application.debug:
        if application.config['MAIL_SERVER']:
            auth = None
            if application.config['MAIL_USERNAME'] and application.config['MAIL_PASSWORD']:
                auth = (application.config['MAIL_USERNAME'], application.config['MAIL_PASSWORD'])
            secure = None
            if application.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(mailhost = (application.config['MAIL_SERVER'], application.config['MAIL_PORT']), fromaddr = 'test@' + application.config['MAIL_SERVER'], toaddrs = application.config['ADMINS'], subject = 'TEST MAIL', credentials = auth, secure = secure, )
            #mail_handler.setLevel(logging.ERROR)
            application.logger.addHandler(mail_handler)
            
    return application

from app import models