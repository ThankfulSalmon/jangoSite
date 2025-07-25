from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime

# Создаём объекты расширений
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

# Фабричная функция
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Привязываем расширения к приложению
    db.init_app(app)
    login_manager.init_app(app)

    # Импортируем и регистрируем blueprint
    from myblog.routes import bp
    app.register_blueprint(bp)

    # Создаём таблицы
    with app.app_context():
        db.create_all()

    return app

# Модель User (нужна для login_manager)
from myblog.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))