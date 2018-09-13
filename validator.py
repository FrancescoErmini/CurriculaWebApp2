from flask import Flask, request, jsonify
from models import  db, Curricula, Courses, Groups, Academicyears, GroupsCourses, CurriculaGroups, Students, Studyplans, StudyplansCourses
from functools import wraps

def validate_curriculum(fn):
	@wraps(fn)
	def decorated_view(*args, **kwargs):
		curriculum_id = kwargs['curriculum_id']
		curriculum = Curricula.query.get(curriculum_id)

		''' Curriculum must has at least one group '''
		if (len(curriculum.groups) < 1 ):
			return jsonify({"error": "curriculum " + str(curriculum.name) + " has zero groups"}), 500

		''' Courses '''
		for group in curriculum.groups:
			if len(group.courses) < group.n:
				return jsonify({"error": "group " + str(group.name) + " has " + str(len(group.courses)) + " courses but " + str(group.n) + " courses are expected."}), 500

		uniqueCourses = []
		for group in curriculum.groups:
			for course in group.courses:
				pass
		return fn(*args, **kwargs)
	return decorated_view

def validate_group(fn):
	@wraps(fn)
	def decorated_view(*args, **kwargs):
		group_id = kwargs['group_id']
		group = Groups.query.get(group_id)

		''' Courses '''
		for course in group.courses:
			if len(group.courses) < group.n:
				return jsonify({"error": "group " + str(group.name) + " has " + str(len(group.courses)) + " courses but " + str(group.n) + " courses are expected."}), 500

		uniqueCourses = []
		for group in curriculum.groups:
			for course in group.courses:
				pass

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

       # if len(data['courses']) > len(set(data['courses'])):
        #	return jsonify({"error": "duplicate courses"}),500

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