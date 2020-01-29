from .auth import auth_blueprint
from .operation import operation_blueprint


def init_app(app):
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(operation_blueprint)
