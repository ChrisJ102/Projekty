from flask import Flask, render_template
from flask_celeryext import FlaskCeleryExt
from flask_login import LoginManager
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from movies_api_app.flask_celery import make_celery


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
ext_celery = FlaskCeleryExt(create_celery_app=make_celery)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    ext_celery.init_app(app)
    login_manager.init_app(app)

    from movies_api_app.directors import directors_bp
    from movies_api_app.errors import errors_bp
    from movies_api_app.movies import movies_bp
    from movies_api_app.auth import auth_bp
    from movies_api_app.category import category_bp
    from movies_api_app.publishing_house import publish_house_bp
    from movies_api_app.loans import loans_bp
    from movies_api_app.orders import orders_bp
    from movies_api_app.shops import shops_bp
    from movies_api_app.moviesinshop import moviesinship_bp

    app.register_blueprint(errors_bp)
    app.register_blueprint(directors_bp, url_prefix='/api/v1')
    app.register_blueprint(movies_bp, url_prefix='/api/v1')
    app.register_blueprint(loans_bp, url_prefix='/api/v1')
    app.register_blueprint(category_bp, url_prefix='/api/v1')
    app.register_blueprint(orders_bp, url_prefix='/api/v1')
    app.register_blueprint(publish_house_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(shops_bp, url_prefix='/api/v1')
    app.register_blueprint(moviesinship_bp, url_prefix='/api/v1')

    @app.route("/")
    def base():
        return render_template("base.html")

    return app
