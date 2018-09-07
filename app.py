from flask import Flask, flash, redirect, render_template, request, url_for, jsonify, json
from models import  db, Curricula, Courses, Groups, Academicyears, GroupsCourses, CurriculaGroups, Students, Studyplans, StudyplansCourses
from functools import wraps
from flask_expects_json import expects_json
from flask_basicauth import BasicAuth
#from validators import  validateallconstraints, validateconstraints
#from schemas import allconstraints_schema, curriculum_schema, group_schema, course_schema, courses_schema, constraint_schema, constraints_schema, studyplan_schema
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

@app.route('/')
def init():
	return render_template('index.html')

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
POST   | /curriculum/courses/                                                           | constraints_schema  	| constraints_schema  |  create new courses constraints for a curriculum 
PUT    | /curriculum/<int:curriculum_id>/course/<string:course_id>/group/<int:group_id>	| constraint_schema  	| constraint_schema   |  update a course constraint 
DELETE | /curriculum/<int:curriculum_id>/course/<string:course_id>/group/<int:group_id> |					  	| constraint_schema   |  delete a course constraint                              

POST   | /studyplan/						| studyplan_schema |  studyplan_schema | submit the studyplan to validate courses.
'''


@app.route('/academicyear/', methods=['GET'])
def getAcademicyears():
    return jsonify({"academicyears":[{ "id": ac.id, "start": ac.start, "end": ac.end } for ac in Academicyears.query.all()]})

@app.route('/academicyear/', methods=['POST'])
@basic_auth.required
#@expects_json(curriculum_schema)
def setAcademicyear():
	try:
		data = request.get_json()	
		academicyear = Academicyears(id=data['id'])
		if data['start'] is not None:
			academicyear.start = data['start']
			academicyear.end = data['end']
		db.session.add(academicyear)
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify(data),201

@app.route('/academicyear/<string:academicyear_id>/', methods=['PUT'])
@basic_auth.required
#@expects_json(curriculum_schema)
def updateAcademicyear(academicyear_id):
	try:
		data = request.get_json()
		academicyear = Academicyears.query.get(academicyear_id)
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
    return jsonify({"courses":[{ "id": c.id, "name":c.name, "cfu":c.cfu, "ac":c.ac, "year":c.year, "semester":c.semester, "ssd":c.ssd, "url":c.url } for c in Courses.query.all()]})


@app.route('/course/', methods=['POST'])
@basic_auth.required
#@expects_json(course_schema)
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

@app.route('/course/<string:course_id>/', methods=['PUT'])
@basic_auth.required
def updateCourse(course_id):
	try:
		d = request.get_json()
		course = Courses.query.get(course_id)
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
#@basic_auth.required
def deleteCourse(course_id):
	try:
		course = Courses.query.get(course_id)
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
    return jsonify({"curricula":[{ "id": c.id, "title":c.title, "desc":c.desc, "ac":c.ac} for c in Curricula.query.order_by(Curricula.id).all()]})

@app.route('/curriculum/', methods=['POST'])
@basic_auth.required
#@expects_json(curriculum_schema)
def setCurriculum():
	try:
		data = request.get_json()	
		curriculum=Curricula(title=data['title'], desc=data['desc'], ac=data['ac'])
		#for g in Groups.query.filter_by(id=[_id.id for _id in data['groups']])
		#	curriculum.groups.append(g)
		db.session.add(curriculum)
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify(data),201

@app.route('/curriculum/<int:curriculum_id>/', methods=['PUT'])
@basic_auth.required
#@expects_json(curriculum_schema)
def updateCurriculum(curriculum_id):
	try:
		data = request.get_json()
		curriculum = Curricula.query.get(curriculum_id)
		curriculum.title = data['title']
		curriculum.desc = data['desc']
		curriculum.ac = data['ac']
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify(data),201

@app.route('/curriculum/<int:curriculum_id>/', methods=['DELETE'])
@basic_auth.required
def deleteCurriculum(curriculum_id):	
	#notice: no check for duplicate
	try:
		curriculum = Curricula.query.get(curriculum_id)
		db.session.delete(curriculum)
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id":curriculum.id, "title":curriculum.title, "desc":curriculum.desc, "ac":curriculum.ac}),201

'''

GROUP

'''

@app.route('/group/', methods=['GET'])
def getGroups():
	return jsonify({"groups":[{ "id": g.id,"name":g.name, "cfu":g.cfu, "n":g.n } for g in Groups.query.order_by(Groups.id).all()]})

@app.route('/group/', methods=['POST'])
@basic_auth.required
#@expects_json(group_schema)
def setGroup():
	try:
		data = request.get_json()
		group = Groups(name=data['name'])
		group.cfu = data['cfu']
		group.n = data['n']
		db.session.add(group)
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify(data),201

@app.route('/group/<int:group_id>/', methods=['PUT'])
@basic_auth.required
#@expects_json(group_schema)
def updateGroup(group_id):
	try:
		data = request.get_json()	
		group = Groups.query.get(group_id)
		group.n = data['n']
		group.cfu = data['cfu']
		group.name = data['name']
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify(data),201

@app.route('/group/<int:group_id>/', methods=['DELETE'])
@basic_auth.required
def deleteGroup(group_id):
	try:
		group = Groups.query.get(group_id)
		db.session.delete(group)
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id":group.id, "cfu":group.cfu, "n":group.n}),201


'''

CONSTRAINTS


'''
@app.route('/group/<int:group_id>/courses/', methods=['GET'])
def getGroupsCourses(group_id):
	try:
		group = Groups.query.get(group_id)
		
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id": group.id, "name": group.name, "cfu": group.cfu, "n": group.n, "courses": [{"id": c.id, "name": c.name} for c in group.courses]})

@app.route('/group/<int:group_id>/courses/', methods=['POST'])
@basic_auth.required
def setGroupsCourses(group_id):
	try:
		data = request.get_json()
		group = Groups.query.get(group_id)
		for c in data['courses']:

			course = Courses.query.get(c['id'])
			group.courses.append(course)
		db.session.add(group)
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify(data),201
'''
@app.route('/group/<int:group_id>/course/<string:course_id>/', methods=['PUT'])
@basic_auth.required
@expects_json(group_schema)
def updateGroupsCourses(group_id):
	try:
		data = request.get_json()	
		group = Groups.query.get(group_id)

		group.n = data['n']
		group.cfu = data['cfu']
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify(data),201
'''
@app.route('/group/<int:group_id>/courses/<string:course_id>/', methods=['DELETE'])
@basic_auth.required
def deleteGroupsCourses(group_id, course_id):
	try:
		group = Groups.query.get(group_id)
		course = Courses.query.get(course_id)
		group.courses.remove(course);
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id": course.id}),201






@app.route('/curriculum/<int:curriculum_id>/groups/', methods=['GET'])
def getCurriculumGroups(curriculum_id):
	try:
		curriculum = Curricula.query.get(curriculum_id)
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id": curriculum.id, "title": curriculum.title, "groups": [{"id": g.id, "name": g.name} for g in curriculum.groups]})

@app.route('/curriculum/<int:curriculum_id>/groups/', methods=['POST'])
@basic_auth.required
def setCurriculumGroups(curriculum_id):
	try:
		data = request.get_json()
		curriculum = Curricula.query.get(curriculum_id)
		for g in data['groups']:
			group = Groups.query.get(g['id'])
			curriculum.groups.append(group)
		db.session.add(curriculum)
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify(data),201

@app.route('/curriculum/<int:curriculum_id>/groups/<int:group_id>/', methods=['DELETE'])
@basic_auth.required
def deleteCurriculumGroups(curriculum_id, group_id):
	try:
		curriculum = Curricula.query.get(curriculum_id)
		group = Groups.query.get(group_id)
		curriculum.groups.remove(group);
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id": group.id}),201


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
#@expects_json(group_schema)
def setStudent():
	try:
		data = request.get_json()
		#if Students.query.get(data['id']) is not None:
		student = Students(id=data['id'])
		student.firstname = data['firstname']
		student.lastname = data['lastname']
		db.session.add(student)
		db.session.commit()
		'''else:
			student = Students.query.get(data['id'])
			student.firstname = data['firstname']
			student.lastname = data['lastname']
	'''
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id": student.id, "firstname": student.firstname, "lastname": student.lastname}),201
'''

@app.route('/student/<string:student_id>/', methods=['DELETE'])
def deleteStudent(group_id):
	try:
		student = Students.query.get(student_id)
		studyplan = Students.query.get(student_id)
		db.session.delete(studyplan)
		db.session.delete(student)
		db.session.commit()
	except Exception as e:
		return jsonify({"error": str(e)}),500
	return jsonify({"id":group.id, "cfu":group.cfu, "n":group.n}),201
'''





@app.route('/studyplan/', methods=['POST'])
def setStudyplan():
	try:
		data = request.get_json() 
		studyplan = Studyplans( id=data['student'], curriculum_id=data['curriculum'])
		for c in data['courses']:
			course = Courses.query.get(c['id'])
			studyplan.courses.append(course)

		db.session.add(studyplan)
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

#	return jsonify({"curriculum":curriculum.id, "title":curriculum.title, "groups":[{"id": g.id, "cfu":g.cfu, "n":g.n, "courses": [{"code": k.id, "name": k.name, "ssd": k.ssd, "url":k.url, "cfu": k.credits, "key": k.key} for k in q if k.group_id == g.id]} for g in groups]}),201


if __name__ == '__main__':
    app.run(debug=True)