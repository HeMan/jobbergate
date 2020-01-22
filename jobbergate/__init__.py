# __init__.py


import os

from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_ldap3_login import LDAP3LoginManager


# instantiate the extensions
login_manager = LoginManager()
bcrypt = Bcrypt()
toolbar = DebugToolbarExtension()
bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()
ldap_manager = LDAP3LoginManager()

users = {}


def create_app(script_info=None):
    import jobbergate.cli

    # instantiate the app
    app = Flask(__name__, template_folder="../apps", static_folder="static")

    # set config
    app_settings = os.getenv("APP_SETTINGS", "jobbergate.config.ProductionConfig")
    app.config.from_object(app_settings)
    from jobbergate.lib import jobbergateconfig

    app.config.update(jobbergateconfig)

    # set up extensions
    login_manager.init_app(app)
    if "LDAP_HOST" in app.config:
        ldap_manager.init_app(app)
    bcrypt.init_app(app)
    toolbar.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprints
    from jobbergate.views import main_blueprint

    app.register_blueprint(main_blueprint)

    # flask login
    from jobbergate.models import User

    login_manager.login_view = "main.login"
    login_manager.login_message_category = "danger"

    @login_manager.user_loader
    def load_user(user_id):
        if user_id in users:
            return users[user_id]
        return None

    @ldap_manager.save_user
    def save_user(dn, username, data, memberships):
        user = User(dn, username, data)
        users[dn] = user
        return user

    # error handlers
    @app.errorhandler(401)
    def unauthorized_page(error):
        return render_template("errors/401.html"), 401

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/500.html"), 500

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {"app": app, "db": db}

    for cmd in jobbergate.cli.cmds:
        app.cli.add_command(cmd)

    return app
