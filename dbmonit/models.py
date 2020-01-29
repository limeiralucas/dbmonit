from __future__ import annotations
import jwt
import logging
import enum
from datetime import timedelta, datetime
from passlib.hash import pbkdf2_sha256 as sha256
from dynaconf import settings
from dbmonit.ext.database import db
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates

logger = logging.getLogger(__name__)

class OperationType(enum.Enum):
    """ Enum specifying possible types of database operations """
    SELECT = 'SELECT'
    UPDATE = 'UPDATE'
    INSERT = 'INSERT'
    UNKNOWN = 'UNKNOWN'

class OperationCategory(enum.Enum):
    """ Enum specifying possible category of database operations """
    READ = 'READ'
    WRITE = 'WRITE'


class User(db.Model, SerializerMixin):
    """ User Model for storing details user"""

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    created_at = db.Column(
        db.DateTime, default=db.func.current_timestamp(), nullable=False
    )

    def __init__(self, username: str, password: str):
        self.username = username
        self.password_hash = sha256.hash(password)

    def generate_token(self) -> str:
        """
        Generates auth token using user data
        :return: string
        """
        try:
            payload = {
                "user_data": self.serialize(),
                "exp": datetime.utcnow() + timedelta(minutes=600),
                "iat": datetime.utcnow(),
            }
            token = jwt.encode(
                payload, settings.JWT_SECRET_KEY, algorithm="HS256"
            ).decode("utf-8")
            return token
        except Exception as e:
            logger.error(e)
            return None

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    def serialize(self) -> str:
        return {"id": self.id, "username": self.username}


class Client(db.Model):
    """ Client Model storing details about clients consuming the api """

    __tablename__ = "client"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    client_secret = db.Column(db.String(256), nullable=False)

    def __init__(self, name):
        self.name = name
        self.client_secret = self.generate_client_secret()

    def generate_client_secret(self) -> str:
        """
        Generates client secret using client data
        :return: string
        """
        try:
            payload = {
                "user_data": self.serialize(),
                "exp": datetime.utcnow() + timedelta(days=365 * 5),
                "iat": datetime.utcnow(),
            }
            token = jwt.encode(
                payload, settings.JWT_SECRET_KEY, algorithm="HS256"
            ).decode("utf-8")
            return token
        except Exception as e:
            logger.error(e)
            return None

    def serialize(self) -> str:
        return {"id": self.id, "name": self.name}


class Operation(db.Model):
    """ Operation Model storing details about each database operation"""

    __tablename__ = "operation"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    operation_type = db.Column(db.Enum(OperationType))
    category = db.Column(db.Enum(OperationCategory))
    table_name = db.Column(db.String(512), nullable=False)
    count = db.Column(db.BigInteger, default=1, nullable=False)
    created_at = db.Column(
        db.DateTime, default=db.func.current_timestamp(), nullable=False
    )

    def __init__(self, operation_type: OperationType, category: OperationCategory, table_name: str):
        self.operation_type = operation_type
        self.category = category
        self.table_name = table_name

    def __repr__(self) -> str:
        return "<Operation (operation_type={}, table_name={})>".format(self.operation_type, self.table_name)
