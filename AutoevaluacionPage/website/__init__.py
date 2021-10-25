from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, login_manager
from flask_mail import Mail


db = SQLAlchemy()
DB_NAME = "database.db"

app = Flask(__name__)
app.config['SECRET_KEY'] = "helloword"
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

mail=Mail(app)

def create_app():
    
    db.init_app(app)
    from . views import views
    from . models import Opciones, Preguntas, Usuarios, Areas, Subgrupos, Admins
    create_database(app)
    app.register_blueprint(views, url_prefix="/")

    login_manager = LoginManager()
    login_manager.login_view = "views.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Admins.query.get(int(id))

    return app

def create_database(app):
    if not path.exists("website/"+DB_NAME):
        db.create_all(app=app)
        print("Created database!")