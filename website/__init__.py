from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_migrate import Migrate
from flask import Flask, render_template, jsonify, json
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'DfGnmvsGTDzzAwAJSEKjVLdtCqwNwvvXnjUVcHNGSmXHuDICMb'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]  # specifying the location of JWT
    app.config["JWT_SECRET_KEY"] = "super-secret-key"
    jwt = JWTManager(app)
    db.init_app(app)
    migrate = Migrate(app, db)


    #todo:
    # Migration
    # Seeds

    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Book, Author, User
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
