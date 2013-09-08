from flask import Flask, request, redirect, render_template, url_for, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from urlparse import urlparse, urljoin
from sqlalchemy.sql.expression import func, select
from sqlalchemy.dialects import postgresql
from sqlalchemy import *
import os
import random
import string
from datetime import date, datetime, timedelta

#################
# Globals
#################
    
try:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['HEROKU_POSTGRESQL_SILVER_URL']
except Exception, e:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://gtfomqcakbtbjc:PqNH-Ltth50qTb6V63gkUJt7uV@ec2-107-21-107-221.compute-1.amazonaws.com:5432/d2n3c81nka07du'
db = SQLAlchemy(app)
metadata = MetaData()

@app.route("/")
def home():    
    # clients = Client.query.all()
    # return render_template("home.html",clients=clients)

@app.route("/client/<id>")
def client(id):
    client = Client.query.filter_by(id=id).first()
    return render_template("client.html", client=client)


@app.route("/client/<id>/progress")
def progress(id):
    client = Client.query.filter_by(id=id).first()
    return render_template("progress.html",client=client)

@app.route("/client/<id>/goals")
def goals(id):
    client = Client.query.filter_by(id=id).first()
    return render_template("goals.html",client=client)

@app.route("/client/<id>/workouts/add")
def workouts_add(id):
    client = Client.query.filter_by(id=id).first()
    client_workouts = client.workouts()
    todays_workouts = [w for w in client_workouts if w.date.date() == datetime.now().date()]
    todays_workouts_names = [w.name for w in todays_workouts]
    top_workouts  = client.top_workouts()
    top_workouts_names = [w[0] for w in top_workouts]
    all_workouts_edited = [w for w in all_workouts if w[0] not in todays_workouts_names and w[0] not in top_workouts_names]
    return render_template("workouts.html",client=client, top_workouts=top_workouts, all_workouts=all_workouts_edited, todays_workouts = todays_workouts)

@app.route("/client/<id>/workouts/edit")
def workouts_edit(id):
    owner_id = int(id)
    client = Client.query.filter_by(id=owner_id).first()
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    time_length_workouts = Time_Length_Workout.query.filter_by(owner_id=owner_id).all()
    rep_set_workouts = Rep_Set_Workout.query.filter_by(owner_id=owner_id).all()
    workouts = time_length_workouts + rep_set_workouts
    todays_workouts = [w for w in workouts if w.date.date() == today]
    yesterdays_workouts = [w for w in workouts if w.date.date() == yesterday]

    all_other_dates = get_all_other_workout_dates(owner_id)
    date_dict = {}
    other_workouts = [w for w in workouts if w.date.date() != yesterday and w.date.date() != today]
    for date in all_other_dates:
        date_dict[date] = []
    for workout in other_workouts:
        date_dict[workout.date.date()].append(workout)
    return render_template("workouts_edit.html", client=client, todays_workouts = todays_workouts, yesterdays_workouts=yesterdays_workouts, other_workouts = date_dict )

   
   
@app.route("/client/<id>/measurements/<edit>")
def measurements(id, edit):
    if edit == "edit":
        edit = True
    else:
        edit = False
    client = Client.query.filter_by(id=id).first()
    todays_measurements = [m for m in client.measurements() if m.date.date() == datetime.now().date()]
    todays_measurements_names = [m.name for m in todays_measurements]
    stock_measurements_edited = [m for m in stock_measurements if m[0] not in todays_measurements_names]
    return render_template("measurements.html",client=client, measurements=stock_measurements_edited, edit=edit, todays_measurements = todays_measurements)

# api

@app.route("/api/add_measurement", methods=['POST'])
def api_add_measurement():
    print 'hey'
    print request.form
    name = request.form['measurement_name']
    value = float(request.form['measurement_value'])
    unit = request.form['measurement_units']
    client_id = int(request.form['client_id'])
    client = Client.query.filter_by(id=client_id).first()
    todays_measurements = [w for w in client.measurements() if w.date.date() == datetime.now().date()]
    todays_measurements_names = [w.name for w in todays_measurements]
    if name in todays_measurements_names:
        this_measurement = [w for w in todays_measurements if w.name == name]
        this_measurement = this_measurement[0]
        this_measurement.value = value
        this_measurement.unit = unit
        db.session.add(this_measurement)
        db.session.commit()
        return jsonify(submitted=True)
    new_measurement = Measurement(name,client)
    new_measurement.value = value
    new_measurement.unit = unit
    new_measurement.date = datetime.now()
    db.session.add(new_measurement)
    db.session.commit()
    return jsonify(submitted=True)


# api
@app.route("/api/add_workout", methods=['POST'])
def api_add_workout():
    print request.form
    print request.form['client_id']
    print request.form['workout_name']
    print request.form['workout_type']
    client_id = int(request.form['client_id'])

    client = Client.query.filter_by(id=client_id).first()
    workout_name = request.form['workout_name']
    workout_type = request.form['workout_type']
    if workout_type == 'Time_Length_Workout':
        try:
            time = timedelta(minutes=float(request.form["workout_time"]))
            length = float(request.form["workout_length"])
        except:
            return jsonify(submitted=False)

    if workout_type == 'Rep_Set_Workout':
        try:
            weights = [float(i) for i in request.form.getlist("weight")]
            reps = [int(i) for i in request.form.getlist("reps")]
        except:
            return jsonify(submitted=False)

    todays_workouts = [w for w in client.workouts() if w.date.date() == datetime.now().date()]
    todays_workouts_names = [w.name for w in todays_workouts]
    if workout_name in todays_workouts_names:
        this_workout = [w for w in todays_workouts if w.name == workout_name]
        this_workout = this_workout[0]
        if workout_type == 'Time_Length_Workout':
            this_workout.time = time
            this_workout.length = length
            db.session.add(this_workout)
            db.session.commit()
            return jsonify(submitted=True)
        if workout_type == 'Rep_Set_Workout':
            this_workout.weights = weights
            this_workout.reps = reps
            this_workout.sets = len(reps)
            db.session.add(this_workout)
            db.session.commit()
            return jsonify(submitted=True)
    
    if workout_type == 'Time_Length_Workout':
        new_workout = Time_Length_Workout(workout_name, client)
        new_workout.time =  time
        new_workout.length = length

    
    if workout_type == 'Rep_Set_Workout':            
        new_workout = Rep_Set_Workout(workout_name, client)
        new_workout.reps = reps
        new_workout.weights = weights
        new_workout.sets = len(reps)
    
    new_workout.date = datetime.now()
    db.session.add(new_workout)
    db.session.commit()
    return jsonify(submitted=True)

@app.route("/client/<id>/workouts/list")
def workout_summary(id):
    owner_id = int(id)
    client = Client.query.filter_by(id=owner_id).first()
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    time_length_workouts = Time_Length_Workout.query.filter_by(owner_id=owner_id).all()
    rep_set_workouts = Rep_Set_Workout.query.filter_by(owner_id=owner_id).all()
    workouts = time_length_workouts + rep_set_workouts
    todays_workouts = [w for w in workouts if w.date.date() == today]
    yesterdays_workouts = [w for w in workouts if w.date.date() == yesterday]

    all_other_dates = get_all_other_workout_dates(owner_id)
    date_dict = {}
    other_workouts = [w for w in workouts if w.date.date() != yesterday and w.date.date() != today]
    for date in all_other_dates:
        date_dict[date] = []
    for workout in other_workouts:
        date_dict[workout.date.date()].append(workout)
    return render_template("workout_summary.html", client=client, todays_workouts = todays_workouts, yesterdays_workouts=yesterdays_workouts, other_workouts = date_dict )

def get_all_other_workout_dates(owner_id):
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    time_length_workouts = Time_Length_Workout.query.filter_by(owner_id=owner_id).all()
    rep_set_workouts = Rep_Set_Workout.query.filter_by(owner_id=owner_id).all()
    workouts = time_length_workouts + rep_set_workouts
    all_dates = set([w.date.date() for w in workouts if w.date.date() != today and w.date.date() != yesterday])
    return all_dates

@app.route("/client/<id>/measurements/list")
def measurement_summary(id):
    owner_id = int(id)
    client = Client.query.filter_by(id=owner_id).first()
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    measurements = Measurement.query.filter_by(owner_id=owner_id).all()
    todays_measurements = [w for w in measurements if w.date.date() == today]
    yesterdays_measurements = [w for w in measurements if w.date.date() == yesterday]

    all_other_dates = get_all_other_measurement_dates(owner_id)
    date_dict = {}
    other_measurements = [w for w in measurements if w.date.date() != yesterday and w.date.date() != today]
    for date in all_other_dates:
        date_dict[date] = []
    for measurement in other_measurements:
        date_dict[measurement.date.date()].append(measurement)
    return render_template("measurement_summary.html", client=client, todays_measurements=measurements,yesterdays_measurements=yesterdays_measurements,other_measurements=date_dict)

def get_all_other_measurement_dates(owner_id):
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    measurements = Measurement.query.filter_by(owner_id=owner_id).all()
    all_measurements = set([w.date.date() for w in measurements if w.date.date() != today and w.date.date() != yesterday])
    return all_measurements

class Course(db.Model):
    __tablename__ = 'courses'
    

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    client_picture_uri = db.Column(db.String(256))

    def __init__(self, firstname, lastname, client_picture_uri='img/profile-photo.jpg'):
        self.firstname = firstname
        self.lastname = lastname
        self.client_picture_uri = client_picture_uri

    def __repr__(self):
        return '<Client %r>' % self.firstname

    def workouts(self):
        this_client_id = self.id
        all_time_length_workouts = Time_Length_Workout.query.filter_by(owner_id=this_client_id).all()
        all_rep_set_workouts = Rep_Set_Workout.query.filter_by(owner_id=this_client_id).all()
        workouts = []
        workouts = all_time_length_workouts + all_rep_set_workouts
        return sorted(workouts, key=lambda x: x.date)

    def top_workouts(self):
        this_client_id = self.id
        counts_time_length_workouts = db.session.query(func.count(Time_Length_Workout.id),Time_Length_Workout.name).group_by(Time_Length_Workout.name).all()
        counts_time_length_workouts = [ (w[0],w[1],'Time_Length_Workout') for w in counts_time_length_workouts]
        counts_rep_set_workouts = db.session.query(func.count(Rep_Set_Workout.id),Rep_Set_Workout.name).group_by(Rep_Set_Workout.name).all()
        counts_rep_set_workouts = [ (w[0],w[1],'Rep_Set_Workout') for w in counts_time_length_workouts]
        counts_workouts = counts_time_length_workouts + counts_rep_set_workouts
        top_workouts = sorted(counts_workouts, key=lambda x: x[0])
        return top_workouts[0:3]  

    def measurements(self):
        this_client_id = self.id
        measurements = Measurement.query.filter_by(owner_id=this_client_id).all()
        print measurements
        return measurements

class Time_Length_Workout(db.Model):
    """
    represents a workout that is measured through distance
    and time. This workout does not implement sets and reps
    """
    __tablename__ = 'time_length_workout'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    owner_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    time = db.Column(db.Interval) # this is length
    length = db.Column(postgresql.FLOAT) # this is time
    date = db.Column(db.DateTime)

    def __init__(self, name,owner):
        self.name = name
        self.owner_id = owner.id
        self.date = datetime.now()

    def __repr__(self):
        return '<Time_Length_Workout %r>' % self.name

class Rep_Set_Workout(db.Model):
    """
    represents a workout that is measured through sets and reps.
    Does not incorporate distance or time.
    """
    __tablename__ = 'rep_set_workout'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    owner_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    sets = db.Column(db.Integer)
    reps = db.Column(postgresql.ARRAY(Integer))
    weights = db.Column(postgresql.ARRAY(postgresql.FLOAT))
    date = db.Column(db.DateTime)

    def __init__(self, name,owner):
        self.name = name
        self.owner_id = owner.id
        self.date = datetime.now()

    def __repr__(self):
        return '<rep_set_workout %r>' % self.name

class Measurement(db.Model):
    """
    Represents a measurement (e.g. waist circumference)
    """
    __tablename__ = 'measurements'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(256))
    owner_id = db.Column(db.Integer,db.ForeignKey('clients.id'))
    value = db.Column(postgresql.FLOAT)
    unit = db.Column(db.String(100))
    date = db.Column(db.DateTime)

    def __init__(self, name,owner):
        self.name = name
        self.owner_id = owner.id

    def __repr__(self):
        return '<Measurement %r>' % self.name


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)