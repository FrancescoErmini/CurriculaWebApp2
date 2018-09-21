#https://pypi.org/project/flask-expects-json/
#https://github.com/Julian/jsonschema

student_schema = {
    'type': 'object',
    'required': ['id'],
    'properties': {
        'id': {'type': 'string'},
        'firstname': {'type': 'string'},
        'lastname': {'type': 'string'}
    }
}

academicyear_schema = {
    'type': 'object',
    'required': ['id'],
    'properties': {
        'id': {'type': 'string'},
        'start': {'type': 'string'},
        'end': {'type': 'string'}
    }
}

course_schema = {
    'type': 'object',
    'required': ['id','name','cfu','ssd'],
    'properties': {
        'id': {'type': 'string'},
        'name': {'type': 'string'},
        'cfu': {'type': 'number'},
        'ssd': {'type': 'string'},
        'year': {'type': 'number'},
        'semester': {'type': 'number'},
        'ac': {'type': 'string'},
        'url': {'type': 'string'}
    }
}

curriculum_schema = {
    'type': 'object',
    'required': ['title', 'desc', 'ac', 'groups'],
    'properties': {
        'title': {'type': 'string'},
        'desc': {'type': 'string'},
        'ac': {'type': 'string'},
        'groups': {
            'type': 'array',
            'items': {
                'type': 'object',
                'required': ['id', 'name'],
                'properties': {
                    'id': {'type': 'number'},
                    'name': {'type': 'string'},
                    'cfu': {'type': 'number'},
                    'n': {'type': 'number'}
                },
                #'additionalProperties': false,
            },
            'minItems': 1 #also checked in validator.py
        }

    }
}

group_schema = {
    'type': 'object',
    'required': ['name','cfu', 'n', 'courses'],
    'properties': {
        'name': {'type': 'string'},
        'cfu': {'type': 'number'},
        'n': {'type': 'number'},
        'courses': {
            'type': 'array',
            'items': {
                'type': 'object',
                'required': ['id', 'name','cfu','ssd'],
                'properties': {
                    'id': {'type': 'string'},
                    'name': {'type': 'string'},
                    'cfu': {'type': 'number'},
                    'ac': {'type': 'string'},
                    'year': {'type': 'number'},
                    'semester': {'type': 'number'},
                    'ssd:': {'type': 'string'},
                    'url': {'type': 'string'},
                },
                #'additionalProperties': false,
            },
            'minItems': 1 #also checked in validator.py
        }
    },
}

studyplan_schema = {
    'type': 'object',
    'required': ['student', 'curriculum', 'courses'],
    'properties': {
        'student': {'type': 'string'},
        'curriculum': {'type': 'number'},
        'courses': {
            'type': 'array',
            'items': {
                'type': 'object',
                'required': ['id','cfu'],
                'properties': {
                    'id': {'type': 'string'},
                    'cfu': {'type':'number'}
                },
                #'additionalProperties': false,
            },
            'minItems': 11
        },
        'othercourses': {
            'type': 'array',
            'items': {
                'type': 'object',
                'required': ['id','name','ssd','cfu'],
                'properties': {
                    'id': {'type': 'string'},
                    'name': {'type': 'string'},
                    'ssd': {'type': 'string'},
                    'cfu': {'type': 'number'}
                },
                #'additionalProperties': false,
            },
            'minItems': 2
        }
    }
}