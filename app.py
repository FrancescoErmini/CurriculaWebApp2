from flask import Flask, flash, redirect, render_template, request, url_for, jsonify, json
from models import  db, Curricula, Courses, Groups, Academicyears,  Students, Studyplans # StudyplansCourses #CurriculaGroups, GroupsCourses,
from functools import wraps
from flask_expects_json import expects_json
from flask_basicauth import BasicAuth
from validator import  validate_studyplan, validate_group, validate_curriculum, validate_academicyear, validate_course, validate_student
from schemas import student_schema, academicyear_schema, curriculum_schema, group_schema, course_schema, studyplan_schema

from flask_cors import CORS, cross_origin
import csv
import os

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

POSTGRES = {
    'user': 'pala',
    'pw': 'wlavela4ever',
    'db': 'pianodistudio2',
    'host': 'localhost',
    'port': '5432',
}

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'admin'



db.init_app(app)
db.create_all(app=app)

basic_auth = BasicAuth(app)


#set manually
#https://github.com/corydolphin/flask-cors/issues/197
@app.after_request
def creds(response):
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


'''		
method | url                                | input json        | output json       | action
GET    | /courses/                          |       -           | course_schema     | list all courses
POST   | /courses/                          | course_schema     | course_schema     | create new courses
PUT    | 
DELETE |

GET    | /curriculum/					  	|                   | curricula_schema  | list all curricula
POST   | /curriculum/					  	| curriculum_schema | curriculum_schema | create a new curriculum
PUT    | /curriculum/<int:curriculum_id>	| curriculum_schema | curriculum_schema | update a curriculum
DELETE | /curriculum/<int:curriculum_id>	|					| curriculum_schema | delete a curriculum

GET    | /group/				            |                   | groups_schema     | list all groups
POST   | /group/			                | groups_schema     | groups_schema     | create a set of groups
PUT    | /group/<int:group_id>	            | group_schema      | group_schema      | update a group
DELETE | /group/<int:group_id>           	|				    | group_schema      | delete a group

GET    | /curriculum/<int:curriculum_id>/courses/                                       | 					  	| constraints_schema  |  list the courses constrinats within a curriculum  

POST   | /studyplan/						| studyplan_schema |  studyplan_schema | submit the studyplan to validate courses.
'''


@app.route('/academicyear/', methods=['GET'])
def getAcademicyears():
	try: 
		academicyears = Academicyears.query.all()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"academicyears":[{ "id": ac.id, "start": ac.start, "end": ac.end } for ac in academicyears ]})

@app.route('/academicyear/', methods=['POST'])
@basic_auth.required
@expects_json(academicyear_schema)
@validate_academicyear
def setAcademicyear():
	try:
		data = request.get_json()	
		academicyear = Academicyears(id=data['id'])
		academicyear.start = data['start']
		academicyear.end = data['end']
		db.session.add(academicyear)
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify(data),201

@app.route('/academicyear/', methods=['PUT'])
@basic_auth.required
@expects_json(academicyear_schema)
@validate_academicyear
def updateAcademicyear():
	try:
		data = request.get_json()
		academicyear = Academicyears.query.get(data['id'])
		academicyear.start = data['start']
		academicyear.end = data['end']
		#notice: no check for dupl]icate
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify(data),201

@app.route('/academicyear/<string:academicyear_id>/', methods=['DELETE'])
@basic_auth.required
def deleteAcademicyear(academicyear_id):	
	#notice: no check for duplicate
	try:
		academicyear = Academicyears.query.get(academicyear_id)
		db.session.delete(academicyear)
		db.session.commit()
	except Exception as e:
		return jsonify({"errors": academicyear_id, "error": str(e)}),500
	return jsonify({"id":academicyear_id}),201


'''

COURSE

'''

@app.route('/course/', methods=['GET'])
def getCourses():
	try:
		courses = Courses.query.all()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"courses":[{ "id": c.id, "name":c.name, "cfu":c.cfu, "ac":c.ac, "year":c.year, "semester":c.semester, "ssd":c.ssd, "url":c.url } for c in courses]}),201


@app.route('/course/', methods=['POST'])
@basic_auth.required
@expects_json(course_schema)
@validate_course
def setCourse():
	try:
		d = request.get_json()
		course = Courses(id=d['id'], name=d['name'], cfu=d['cfu'], ssd=d['ssd'])
		db.session.add(course)
		course.ac= d['ac']
		course.year= d['year']
		course.semester= d['semester']
		course.url= d['url']
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify(d),201

@app.route('/course/', methods=['PUT'])
@basic_auth.required
@expects_json(course_schema)
def updateCourse():
	try:
		d = request.get_json()
		course = Courses.query.get(d['id'])
		course.name = d['name']
		course.cfu= d['cfu']
		course.ssd= d['ssd']
		course.ac= d['ac']
		course.year= d['year']
		course.semester= d['semester']
		course.url= d['url']
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify(d),201

@app.route('/course/<string:course_id>/', methods=['DELETE'])
@basic_auth.required
def deleteCourse(course_id):
	try:
		course = Courses.query.get(course_id)
		#course = db.session.query(Courses).filter(Courses.id == course_id).first()

		db.session.delete(course)
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id": str(course_id)}),201


'''

CURRICULUM

'''

@app.route('/curriculum/', methods=['GET'])
def getCurricula():
    return jsonify({"curricula":[{ "id": curriculum.id, "title":curriculum.title, "desc":curriculum.desc, "ac":curriculum.ac, "groups": [{"id": g.id,"name":g.name, "cfu":g.cfu, "n":g.n} for g in curriculum.groups]} for curriculum in Curricula.query.order_by(Curricula.id).all()]}),201


@app.route('/curriculum/<int:curriculum_id>/', methods=['GET'])
def getCurriculum(curriculum_id):
	try:
		curriculum = Curricula.query.get(curriculum_id)
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({ "id": curriculum.id, "title":curriculum.title, "desc":curriculum.desc, "ac":curriculum.ac, "groups": [{"id": g.id,"name":g.name, "cfu":g.cfu, "n":g.n} for g in curriculum.groups]}),201


@app.route('/curriculum/', methods=['POST'])
@basic_auth.required
@expects_json(curriculum_schema)
@validate_curriculum
def setCurriculum():
	try:
		data = request.get_json()	
		curriculum=Curricula(title=data['title'], desc=data['desc'], ac=data['ac'])
		#for g in Groups.query.filter_by(id=[_id.id for _id in data['groups']])
		#	curriculum.groups.append(g)
		curriculum.groups = []
		for g in data['groups']:
			group = Groups.query.get(g['id'])
			curriculum.groups.append(group)

		db.session.add(curriculum)
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id": curriculum.id}),201

@app.route('/curriculum/<int:curriculum_id>/', methods=['PUT'])
@basic_auth.required
@expects_json(curriculum_schema)
@validate_curriculum
def updateCurriculum(curriculum_id):
	try:
		data = request.get_json()
		curriculum = Curricula.query.get(curriculum_id)
		curriculum.title = data['title']
		curriculum.desc = data['desc']
		curriculum.ac = data['ac']
		curriculum.groups = []
		for g in data['groups']:
			group = Groups.query.get(g['id'])
			curriculum.groups.append(group)
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id": curriculum.id}),201

@app.route('/curriculum/<int:curriculum_id>/', methods=['DELETE'])
@basic_auth.required
def deleteCurriculum(curriculum_id):	
	try:
		curriculum = Curricula.query.get(curriculum_id)
		#my_instance = db.session.query(Curricula).filter(Curricula.id == curriculum_id).first()
		db.session.delete(curriculum)
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id":curriculum.id}),201
'''

GROUP

'''

@app.route('/group/', methods=['GET'])
def getGroups():
	return jsonify({"groups":[{"id": group.id, "name": group.name, "cfu": group.cfu, "n": group.n, "courses": [{ "id": c.id, "name":c.name, "cfu":c.cfu, "ac":c.ac, "year":c.year, "semester":c.semester, "ssd":c.ssd, "url":c.url} for c in group.courses]} for group in Groups.query.order_by(Groups.id).all()] })

@app.route('/group/<int:group_id>/', methods=['GET'])
def getGroup(group_id):
	try:
		group = Groups.query.get(group_id)
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id": group.id, "name": group.name, "cfu": group.cfu, "n": group.n, "courses": [{ "id": c.id, "name":c.name, "cfu":c.cfu, "ac":c.ac, "year":c.year, "semester":c.semester, "ssd":c.ssd, "url":c.url} for c in group.courses]})


@app.route('/group/', methods=['POST'])
@basic_auth.required
@expects_json(group_schema)
@validate_group
def setGroup():
	try:
		data = request.get_json()
		group = Groups(name=data['name'])
		group.cfu = data['cfu']
		group.n = data['n']
		group.courses = []
		for c in data['courses']:

			course = Courses.query.get(c['id'])
			group.courses.append(course)

		db.session.add(group)
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id": group.id}),201

@app.route('/group/<int:group_id>/', methods=['PUT'])
@basic_auth.required
@expects_json(group_schema)
@validate_group
def updateGroup(group_id):
	try:
		data = request.get_json()	
		group = Groups.query.get(group_id)

		group.n = data['n']
		group.cfu = data['cfu']
		group.name = data['name']
		for c in data['courses']:

			course = Courses.query.get(c['id'])
			group.courses.append(course)
			
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id": group.id}),201

@app.route('/group/<int:group_id>/', methods=['DELETE'])
@basic_auth.required
def deleteGroup(group_id):
	try:
		group = Groups.query.get(group_id)
		db.session.delete(group)
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id":group.id}),201



@app.route('/curriculum/<int:curriculum_id>/courses/', methods=['GET'])
def getCurriculumCourses(curriculum_id):
	try:
		curriculum = Curricula.query.get(curriculum_id)

	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"curriculum":{"id": curriculum.id, "title": curriculum.title}, "groups": [{"id": g.id, "name": g.name, "n": g.n, "cfu": g.cfu, "courses": [{"id": c.id, "name": c.name, "ssd": c.ssd, "cfu": c.cfu, "year": c.year, "semester": c.semester, "ac": c.ac, "url": c.url} for c in g.courses]} for g in curriculum.groups]})




@app.route('/student/<string:student_id>/', methods=['GET'])
def getStudent(student_id):
	try:
		student = Students.query.get(student_id)
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id": student.id, "firstname": student.firstname, "lastname": student.lastname}),201

@app.route('/student/', methods=['POST'])
@expects_json(student_schema)
@validate_student
def setStudent():
	try:
		data = request.get_json()
		if Students.query.get(data['id']) is None:
			student = Students(id=data['id'])
			student.firstname = data['firstname']
			student.lastname = data['lastname']
			db.session.add(student)
			db.session.commit()
		else:
			student = Students.query.get(data['id'])
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id": student.id, "firstname": student.firstname, "lastname": student.lastname}),201




@app.route('/studyplan/', methods=['POST'])
@expects_json(studyplan_schema)
@validate_studyplan
def setStudyplan():
	try:
		data = request.get_json() 

		if Studyplans.query.get(data['student']) is None:
			studyplan = Studyplans( id=data['student'], curriculum_id=data['curriculum'])
			db.session.add(studyplan)
		else:
			studyplan = Studyplans.query.get(data['student'])

		for c in data['courses']:
			course = Courses.query.get(c['id'])
			studyplan.courses.append(course)

		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify(data),201

@app.route('/studyplan/<string:student_id>/', methods=['GET'])
def getStudyplan(student_id):
	try: 
		studyplan = Studyplans.query.get(student_id)
		student = Students.query.get(student_id)
		curriculum = Curricula.query.get(studyplan.curriculum_id)

	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id": studyplan.id, "student": {"id": student.id, "firstname": student.firstname, "lastname": student.lastname }, "curriculum": {"id": curriculum.id, "title": curriculum.title, "ac": curriculum.ac}, "courses": [{"id": c.id, "name": c.name, "ssd": c.ssd, "url": c.url, "cfu": c.cfu, "year": c.year, "semester": c.semester} for c in studyplan.courses ] }),201	

@app.route('/studyplan/<string:student_id>/', methods=['DELETE'])
def deleteStudyplan(student_id):
	try: 
		studyplan = Studyplans.query.get(student_id)
		db.session.delete(studyplan)
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id": studyplan.id }), 201


if __name__ == '__main__':
    app.run(debug=True)