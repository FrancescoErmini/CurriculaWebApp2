from flask import Flask, request, jsonify
from models import  db, Curricula, Courses, Groups, Academicyears, Students, Studyplans, OtherCourses #, StudyplansCourses #  CurriculaGroups, GroupsCourses,
from functools import wraps
import string

def validate_curriculum(fn):
	@wraps(fn)
	def decorated_view(*args, **kwargs):
		
		curriculum	= request.get_json()

		if curriculum['title'] == "":
			return jsonify({"error": "title can not be empty"}), 500

		if len(curriculum['groups']) == 0 :
			return jsonify({"error": "No groups. specified. Create groups first, then specify curriculum groups."}), 500


		uniqueCourses = []
		for g in curriculum['groups']:
			group = Groups.query.get(g['id'])
			for course in group.courses:
				if course.id not in uniqueCourses:
					uniqueCourses.append(course.id)
				else:
					return jsonify({"error": "duplicate courses in curriculum" + str(len(uniqueCourses))}),500
		return fn(*args, **kwargs)
	return decorated_view

def validate_group(fn):
	@wraps(fn)
	def decorated_view(*args, **kwargs):
		
		group =	request.get_json()

		if len(group['courses']) < 1:
			return jsonify({"error":"No courses specified. Create course first, then specify group courses."}), 500
		
		if group['n'] < 1:
			return jsonify({"error":"N must be a positive number"}), 500

		if len(group['courses']) <= group['n']:
			return jsonify({"error": "group has " + str(len(group['courses'])) + " courses but " + str(group['n']) + " courses are expected."}), 500

		uniqueCourses = []
		for course in group['courses']:
			if course['id'] not in uniqueCourses:
				uniqueCourses.append(course['id'])
			else:
				return jsonify({"error":"duplicate course in group"}),500

		return fn(*args, **kwargs)
	return decorated_view

''' STUDY PLAN '''

def validate_studyplan(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
    	if not request.data:
    		return jsonify({"error": "no json input"}), 404
        data = request.get_json()
        curriculum = Curricula.query.get(data['curriculum'])

        uniqueCourses = []
        for course in data['courses']:
        	if course['id'] not in uniqueCourses:
        		uniqueCourses.append(course['id'])
        	else:
        		return  jsonify({"error": "duplicate courses"}),500

        for group in curriculum.groups:
        	count=0
        	for course in data['courses']:
        		if( course['id'] in [c.id for c in group.courses]):
        			count+=1
        	if count < group.n:
        		return jsonify({"error": "group " + str(group.name) +" has " +str(count)+" courses but " + str(group.n) + " courses are expected for curriculum " +  str(curriculum.title) }),500

        return fn(*args, **kwargs)
    return decorated_view

def validate_academicyear(fn):
	@wraps(fn)
	def decorated_view(*args, **kwargs): 
		data = request.get_json()
		academicyear = data['id']
		years = string.split(academicyear, '-')
		if academicyear == "":
			return jsonify({"error":"Academic year can not be empty"}),500
		if len(years) < 2:
			return jsonify({"error":"Wrong format. use minus char - to separate years"}),500
		if int(years[0]) < 2018 or int(years[0]) > 2021:
			return jsonify({"error": "Year must be in range [2018,2021] "}),500
		if (int(years[0]) + 1) != int(years[1]):
			return jsonify({"error": "Year not in format [<year>-<year+1>]" }),500

		return fn(*args, **kwargs)
	return decorated_view

'''
course id string empty "" create probmes in delete api because it becomes /courses/delete//
'''
def validate_course(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        data = request.get_json()
        course_id = data['id']
        if course_id == "":
        	return jsonify({"error":"Course code can not be empty"}),500
        if len(course_id) != 7:
        	return jsonify({"error":"Course code is 7 char length"}),500
        else:
        	pass
        return fn(*args, **kwargs)
    return decorated_view

'''
student data validation
'''
def validate_student(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
    
        data = request.get_json()
        student_id = data['id']
        if student_id == "":
        	return jsonify({"error":"Student id can not be empty"}),500
        if len(student_id) != 7:
        	return jsonify({"error":"Student id is 7 char length"}),500
        else:
        	pass
        return fn(*args, **kwargs)
    return decorated_view