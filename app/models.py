from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

class Course(db.Model):
    id = db.Column(db.Integer, primary_key = True)

    prefix_name = db.Column(db.String(150), index = True, unique = True)
    name = db.Column(db.String(150), index = True, unique = True)
    class_code = db.Column(db.String(150), index = True)
    class_number = db.Column(db.String(150), index = True)
    class_section = db.Column(db.String(150), index = True)
    term = db.Column(db.String(150), index = True)
    year = db.Column(db.String(150), index = True)
    program = db.Column(db.String(150), index = True)
    instructor = db.Column(db.String(150), index = True)
    instructor_email = db.Column(db.String(150), index = True)
    credits = db.Column(db.String(150), index = True)
    grade_type = db.Column(db.String(150), index = True)
    status = db.Column(db.String(150), index = True)
    clock_hours = db.Column(db.String(150), index = True)
    waitlist_available = db.Column(db.Boolean, index = True)
    course_days = db.Column(db.String(150), index = True)
    course_times = db.Column(db.PickleType) # array of date time objects
    course_location = db.Column(db.String(150), index = True, unique = True)
    course_description = db.Column(db.Text, index = True, unique = True)



    # prereqs = db.relationship('Course', backref = 'course', lazy = 'dynamic')
    
    def __repr__(self):
        return '<User %r>' % (self.nickname)    
        
# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     body = db.Column(db.String(140))
#     timestamp = db.Column(db.DateTime)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

#     def __repr__(self):
#         return '<Post %r>' % (self.body)