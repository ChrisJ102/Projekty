from flask import Flask, render_template
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from Apteka_app.klienci import klienci_bp
    from Apteka_app.recepta import recepta_bp
    from Apteka_app.stanowiska import stanowiska_bp
    from Apteka_app.producent import producent_bp
    from Apteka_app.pracownicy import pracownicy_bp
    from Apteka_app.produkty import produkty_bp
    from Apteka_app.transakcja import transakcja_bp

    app.register_blueprint(klienci_bp, url_prefix='/aptekaapp')
    app.register_blueprint(recepta_bp, url_prefix='/aptekaapp')
    app.register_blueprint(stanowiska_bp, url_prefix='/aptekaapp')
    app.register_blueprint(producent_bp, url_prefix='/aptekaapp')
    app.register_blueprint(pracownicy_bp, url_prefix='/aptekaapp')
    app.register_blueprint(produkty_bp, url_prefix='/aptekaapp')
    app.register_blueprint(transakcja_bp, url_prefix='/aptekaapp')

    @app.route("/")
    def base():
        return render_template("base.html")

    return app