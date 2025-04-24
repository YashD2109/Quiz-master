#Import the object for database creation
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime ,timezone
from flask_login import UserMixin

db = SQLAlchemy()


# Admin table
class Admin(db.Model):
    __tablename__ = 'Admin'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

# User table
class User(db.Model,UserMixin):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    qualification = db.Column(db.String(100), nullable=True)
    dob = db.Column(db.Date, nullable=False)
    allow = db.Column(db.Boolean, nullable=False, default=False)

# Subject table
class Subject(db.Model):
    __tablename__ = 'Subject'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade='all, delete-orphan')


# Chapter table
class Chapter(db.Model):
    __tablename__ = 'Chapter'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('Subject.id', ondelete='CASCADE'), nullable=False)
    

# Quiz table
class Quiz(db.Model):
    __tablename__ = 'Quiz'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    chapter_id = db.Column(db.Integer, db.ForeignKey('Chapter.id', ondelete='CASCADE'), nullable=False)
    # date of the quiz
    create_date = db.Column(db.DateTime, default=datetime.now(timezone.utc)) 
    startline = db.Column(db.DateTime, nullable=False)
    # t otal score of the quiz
    total_score = db.Column(db.Integer, nullable=False,default =0) 
    # duration of quiz
    duration = db.Column(db.Integer, nullable=False) 
    deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="draft")
    approved = db.Column(db.Boolean, nullable=False, default=False)
     # Define the relationship to UserAnswer
    user_answers = db.relationship('UserAnswer', back_populates='quiz')
# Questions table
class Questions(db.Model):
    __tablename__ = 'Questions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    index = db.Column(db.Integer,autoincrement=True,default=0)
    text = db.Column(db.Text, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('Quiz.id', ondelete='CASCADE'), nullable=False)
    option1 = db.Column(db.String(255), nullable=False)
    option2 = db.Column(db.String(255), nullable=False)
    option3 = db.Column(db.String(255), nullable=False)
    option4 = db.Column(db.String(255), nullable=False)
    # Stores the correct option (1, 2, 3, or 4)
    correct_option = db.Column(db.Integer, nullable=False)
    # marks for the question
    marks = db.Column(db.Integer, nullable=False)  

# Scores table
class Scores(db.Model):
    __tablename__ = 'Scores'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id', ondelete='CASCADE'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('Quiz.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Integer,default = 0)
    status = db.Column(db.String(50), nullable=False, default="Not_Attempted")

class UserAnswer(db.Model):
    __tablename__ = 'UserAnswer'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('Quiz.id', ondelete='CASCADE'), nullable=False)
    selected_answer = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Integer,nullable=False)
    quiz = db.relationship('Quiz', back_populates='user_answers')

    

    def __repr__(self):
        return f'<UserAnswer {self.id}, User {self.user_id}, Quiz {self.quiz_id}>'


# class for flask login
class UserLogin(UserMixin):
    def __init__(self, id, role, email):
        self.id = id
        self.role = role
        self.email= email