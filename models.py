from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin


db = SQLAlchemy()


class Projects(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=True)
    homepage_thumbnail = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable= True)
    video_url = db.Column(db.String(250),  nullable= True)
    category = db.Column(db.String(250), nullable=True)
    tech_used = db.Column(db.String(250), nullable=True)
    project_url = db.Column(db.String(250), nullable=True, unique=True)
    description = db.Column(db.String(250), nullable=True)

    # Helper function to convert model instances to dictionaries
    def to_dict(self):
        # Method 1.
        dictionary = {}
        # # Loop through each column in the data record
        # for column in self.__table__.columns:
        #     # Create a new dictionary entry;
        #     # where the key is the name of the column
        #     # and the value is the value of the column
        #     dictionary[column.name] = getattr(self, column.name)
        # return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)
