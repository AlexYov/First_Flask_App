from flask import Flask
from app.config_file import BaseConfig
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import logging
from logging.handlers import SMTPHandler

application = Flask(__name__)
application.config.from_object(BaseConfig)
db = SQLAlchemy(application)
login = LoginManager(application)
login.login_view = 'login'
mail = Mail(application)

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

from app import routes, models, errors