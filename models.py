from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

class Feedback(db.Model):
    __tablename__ = "feedback_posts"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    title = db.Column(db.String(100), nullable = False)
    content = db.Column(db.Text, nullable = False)
    username = db.Column(db.Text, db.ForeignKey('users.username'))

    user = db.relationship('User', backref = 'feedback')

class User(db.Model):

    __tablename__ = "users"

    username = db.Column(db.String(20), primary_key = True, unique = True, nullable = False)
    password = db.Column(db.Text, nullable = False)
    email = db.Column(db.String(50), nullable = False, unique = True)
    first_name = db.Column(db.String(30), nullable = False)
    last_name = db.Column(db.String(30), nullable = False)

    @classmethod
    def register(cls, username, pwd, email , first_name , last_name):
        hashed = bcrypt.generate_password_hash(pwd)
        hashed_utf8 = hashed.decode("utf8")
        return cls(username = username, password = hashed_utf8, email = email, first_name = first_name, last_name = last_name)

    @classmethod
    def authenticate(cls, username, pwd):
        # Validate that user exists and password is correct
        u = User.query.filter_by(username = username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # Return user instance
            return u
        else: 
            return False
