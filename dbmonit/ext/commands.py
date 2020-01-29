import click
from dbmonit.ext.database import db
from dbmonit.models import User, Client


def create_db():
    """Creates database"""
    db.create_all()


def drop_db():
    """Cleans database"""
    db.drop_all()


def create_user(username, password):
    """ Register a new user if it has not been created """
    if User.query.filter_by(username=username).first():
        raise RuntimeError(f"{username} ja esta cadastrado")
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return user

def create_client(name):
    """ Register a new client """
    client = Client(name=name)
    print(client.client_secret)
    db.session.add(client)
    db.session.commit()
    return client

def init_app(app):
    # add a single command
    @app.cli.command()
    @click.option("--username", "-u")
    @click.option("--password", "-p")
    def add_user(username, password):
        """Adds a new user to the database"""
        return create_user(username, password)

    @app.cli.command()
    @click.option("--name", "-n")
    def add_client(name):
        """Adds a new client to the database"""
        return create_client(name)
