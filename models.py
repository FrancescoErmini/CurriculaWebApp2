#!/usr/bin/env python
from flask_sqlalchemy import SQLAlchemy
import datetime


# create a new SQLAlchemy object

db = SQLAlchemy()

# Base model that for other models to inherit from 
class Base(db.Model):
	__abstract__ = True

'''
Groups: Parent
Course: child
GroupsCourses: Association
http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#association-object

>>> s = Session()
>>> group1 = Groups(name='gruppo-inf-inteligent')
>>> course1 = Courses(id='b000001', name="corso1")
>>> group1.courses.append(course1)
>>> s.add(group1)
>>> s.commit()
'''
class Groups(Base):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    n = db.Column(db.Integer, nullable=False)
    cfu = db.Column(db.Integer)

    courses = db.relationship('Courses', secondary='groups_courses_association')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

class Courses(Base):
    __tablename__ = 'courses'
    id = db.Column(db.String(7), primary_key=True) # id = B000001
    name = db.Column(db.String(200), nullable=False)               # name = Analisi Matematica
    cfu = db.Column(db.Integer, nullable=False)
    ssd = db.Column(db.String(10), nullable=False)
    year = db.Column(db.Integer,  nullable=True)
    semester = db.Column(db.Integer, nullable=True)
    url = db.Column(db.String(100), nullable=True)
    ac = db.Column(db.String(9), db.ForeignKey('academicyears.id'))
    #academicyears = db.relationship('Academicyears',foreign_keys=[ac])

    def __init__(self, id, name, cfu, ssd):
    	self.id=id
        self.name = name
        self.cfu = cfu
        self.ssd = ssd

class Curricula(Base):
    __tablename__ = 'curricula'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(500), nullable=False)
    ac = db.Column(db.String(9), db.ForeignKey('academicyears.id'))
    desc = db.Column(db.String(2000))

    groups = db.relationship('Groups', secondary='curricula_groups_association')

    def __init__(self, title, ac, desc):
        self.title = title
        self.ac = ac
        self.desc = desc

    def __repr__(self):
        return self.title


class GroupsCourses(Base):
    __tablename__ = 'groups_courses_association'
    #id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer,  db.ForeignKey('groups.id'),  primary_key=True)
    course_id = db.Column(db.String(7), db.ForeignKey('courses.id'),  primary_key=True)
    #group = db.relationship('Groups', foreign_keys=[group_id], backref=db.backref('courses', lazy='dynamic', passive_updates=False))
    #course = db.relationship('Courses', foreign_keys=[course_id])

    def __init__(self, group_id, course_id):
        self.course_id = course_id
        self.group_id = group_id


class CurriculaGroups(Base):
    __tablename__ = 'curricula_groups_association'

    curriculum_id = db.Column(db.Integer, db.ForeignKey('curricula.id'),  primary_key=True)
    group_id = db.Column(db.Integer,  db.ForeignKey('groups.id'),  primary_key=True)

    def __init__(self, curriculum_id, group_id):
        self.curriculum_id = curriculum_id
        self.group_id = group_id

'''

class Constraints(Base):
    __tablename__ = 'constraints'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    curriculum_id = db.Column(db.Integer, db.ForeignKey('curricula.id'))
    course_id = db.Column(db.String(7))
    group_id = db.Column(db.Integer)
    status = db.Column(db.Boolean) # to mark poll as open or closed

	# Relationship declaration (makes it easier for us to access the polls model
	# from the other models it's related to)
	#curriculum = db.relationship('Curricula', foreign_keys=[curriculum_id],
	#	backref=db.backref('courses', lazy='dynamic',passive_updates=False))

	#course = db.relationship('Courses',foreign_keys=[course_id],
	#	backref=db.backref('constraints', lazy='dynamic', passive_updates=False))

    def __init__(self, curriculum_id, group_id, course_id):
    	self.curriculum_id=curriculum_id
    	self.group_id=group_id
    	self.course_id=course_id

    def __repr__(self):
    	return self.course.name

'''
class Students(Base):
    __tablename__ = 'students'
    id = db.Column(db.String(7), primary_key=True)
    firstname = db.Column(db.String(20))
    lastname = db.Column(db.String(20))

    #studyplan = db.relationship('Studyplans', backref=db.backref('students', uselist=False))
    studyplan = db.relationship('Studyplans', uselist=False)


    def __init__(self, id):
        self.id = id
    def __repr__(self):
        return self.id


class Studyplans(Base):
    __tablename__ = 'studyplans'
    id = db.Column(db.String(7), db.ForeignKey('students.id'), primary_key=True)
    curriculum_id = db.Column(db.Integer, db.ForeignKey('curricula.id'))

    
    courses = db.relationship('Courses', secondary='studyplan_courses_association')

    def __init__(self, id, curriculum_id):
        self.id = id
        self.curriculum_id = curriculum_id

class StudyplansCourses(Base):
    __tablename__ = 'studyplan_courses_association'
    studyplan_id = db.Column(db.String(7), db.ForeignKey('studyplans.id'), primary_key=True)
    course_id = db.Column(db.String(7), db.ForeignKey('courses.id'),  primary_key=True)
    #state = db.Column(db.Boolean, default=False)

    def __init__(self, studyplan_id, course_id):
        self.course_id=course_id
        self.studyplan_id=studyplan_id


class Academicyears(Base):
    __tablename__ = 'academicyears'
    id = db.Column(db.String(9), primary_key=True )
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)

    def __init__(self, id):
    	self.id=id

    def __repr__(self):
    	return self.id
