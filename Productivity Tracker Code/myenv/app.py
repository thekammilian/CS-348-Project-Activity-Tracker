from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime


#from SQLAlchemy.orm import sessionmaker
#from SQLAlchemy import create_engine
import hashlib



app = Flask(__name__)
app.secret_key = 'brian_waddell'  # Replace 'your_secret_key' with your own secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productivity_tracker_database.db'
db = SQLAlchemy(app)

migrate = Migrate(app,db)

# Create and bind engine for queries
#engine = create_engine('sqlite:///productivity_tracker_database.db')
#Session = sessionmaker(bind=engine)
# session = Session()

def create_id(variables):
    # Convert the variables to a string for hashing
    data = str(variables).encode('utf-8')

    # Choose a hash algorithm (e.g., SHA-256)
    hash_object = hashlib.sha256(data)

    # Get the hexadecimal representation of the hash
    hex_digest = hash_object.hexdigest()

    # Truncate the hex_digest to four characters
    id_result = int(hex_digest[:4],16)

    return id_result


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #activity_name = db.Column(db.String(255), nullable=False, default='test')
    activity_date = db.Column(db.String(10), nullable=False)
    importance = db.Column(db.Integer, nullable=False)
    time_spent_hrs = db.Column(db.Float, nullable=False)

    # Create an index on the activity_date column
    __table_args__ = (db.Index('idx_activity_date', 'activity_date'),)
    
    @property
    def productivity_score(self):
        return self.importance * self.time_spent_hrs


# Routes and view functions

@app.route('/submit',methods=['POST'])
def login():
    activity_id = request.form['activity_id']
    activity_date = request.form['activity_date']
    importance = request.form['importance']
    time_spent_hrs = request.form['time_spent_hrs']
    
    new_activity = Activity(
        id = activity_id,
        activity_date=activity_date,
        importance=importance,
        time_spent_hrs=time_spent_hrs
    )

    print("new_activity found submit")

    db.session.add(new_activity)
    db.session.commit()

    return redirect(url_for("/"))

@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        
        #activity_id = request.form['activity_id']
        activity_date = request.form['activity_date']
        importance = request.form['importance']
        time_spent_hrs = request.form['time_spent_hrs']

        variables = [activity_date, importance, time_spent_hrs]
        activity_id = create_id(variables=variables)

        id_values = [result[0] for result in db.session.query(Activity.id).all()]
        while (activity_id in id_values):
            activity_id = create_id(variables=variables)
        
        new_activity = Activity(
            id = activity_id,
            activity_date=activity_date,
            importance=importance,
            time_spent_hrs=time_spent_hrs
        )

        print("new_activity found /")

        db.session.add(new_activity)
        db.session.commit()

        activities = Activity.query.all()  # Retrieve all activities from the database

        return render_template("index.html", activities=activities, summary_data=summary(activities))

        #flash('New activity added successfully')
    

    activities = Activity.query.all()  # Retrieve all activities from the database
    
    #printing out activities (this works)
    for a in activities: 
        print(f"ID: {a.id}, Activity Date: {a.activity_date}, Productivity score: {a.productivity_score}") 

    #return template with activities
    return render_template('index.html',activities=activities, summary_data=summary(activities))

@app.route('/filter', methods=['POST'])
def filter_activity():
    filter_activity_id = request.form.get('filter_activity_id')
    filter_activity_id = int(filter_activity_id) if filter_activity_id and filter_activity_id.isdigit() else None

    filter_date = request.form.get('filter_date')
    filter_importance = request.form.get('filter_importance')
    filter_importance = int(filter_importance) if filter_importance and filter_importance.isdigit() else None

    filter_time_spent_hrs = request.form.get('filter_time_spent_hrs')

    filter_productivity = request.form.get('filter_productivity')

    # Start building the base query
    query = Activity.query

    # Apply filters based on provided values
    if filter_activity_id:
        query = query.filter(Activity.id == filter_activity_id)

    if filter_date:
        query = query.filter(Activity.activity_date == filter_date)

    if filter_importance:
        query = query.filter(Activity.importance == filter_importance)

    if filter_time_spent_hrs:
        query = query.filter(Activity.time_spent_hrs == filter_time_spent_hrs)

    if filter_productivity:
        query = query.filter(Activity.productivity_score == filter_productivity)


    # Execute the query and retrieve the filtered activities
    filtered_activities = query.all()
    for a in filtered_activities: 
        print(f"ID: {a.id}, Activity Date: {a.activity_date}, Productivity score: {a.productivity_score}") 

    filtered_summary = summary(filtered_activities)
    # Return or render the filtered activities as needed
    return render_template('index.html', activities=filtered_activities, summary_data=filtered_summary)

@app.route('/edit', methods=['POST'])
def edit_activity():
    # Get values from the form submission
    edit_activity_id = request.form.get('edit_activity_id')
    edit_date = request.form.get('edit_date')
    edit_importance = int(request.form.get('edit_importance'))
    edit_time_spent_hrs = float(request.form.get('edit_time_spent_hrs'))
    edit_productivity = edit_importance * edit_time_spent_hrs

    # Ensure the activity_id is valid
    try:
        edit_activity_id = int(edit_activity_id)
    except ValueError:
        # Handle invalid activity_id (not an integer)
        return redirect(url_for('index.html'))

    # Retrieve the existing activity from the database
    activity_to_edit = Activity.query.get(edit_activity_id)

    if activity_to_edit:
        # Update the activity attributes
        activity_to_edit.activity_date = edit_date
        activity_to_edit.importance = edit_importance
        activity_to_edit.time_spent_hrs = edit_time_spent_hrs
        activity_to_edit.productivity = edit_productivity

        # Commit the changes to the database
        db.session.commit()

        # Redirect to the main page or a success page
        return render_template('index.html',activities=Activity.query.all(), summary_data=summary(Activity.query.all()))
    
    return redirect(url_for('index.html'))

from flask import flash

@app.route('/delete/<int:activity_id>', methods=['GET'])
def delete_activity(activity_id):
    activity = Activity.query.get(activity_id)
    
    if activity:
        db.session.delete(activity)
        db.session.commit()
        flash('Activity deleted successfully')
    else:
        flash('Activity not found')

    return redirect(url_for('index'))

def summary(activities):

    # Calculate the summary statistics based on the activities data
    record_count = len(activities)
    
    if activities:
        dates = (activity.activity_date for activity in activities)
        date_objects = [datetime.strptime(date_str, "%m-%d-%Y") for date_str in dates]
        sorted_dates = sorted(date_objects)

        earliest_date = sorted_dates[0].strftime("%m-%d-%Y")
        latest_date = sorted_dates[-1].strftime("%m-%d-%Y")

        avg_importance = sum(activity.importance for activity in activities) / record_count
        avg_time_spent = sum(activity.time_spent_hrs for activity in activities) / record_count
        avg_productivity_score = sum(activity.productivity_score for activity in activities) / record_count
    else:
        earliest_date = latest_date = avg_importance = avg_time_spent = avg_productivity_score = 0

    # Prepare the data for rendering in the template
    summary_dict = {
        'record_count': record_count,
        'earliest_date': earliest_date,
        'latest_date': latest_date,
        'avg_importance': round(avg_importance, 2),
        'avg_time_spent': round(avg_time_spent, 2),
        'avg_productivity_score': round(avg_productivity_score, 2),
        'activities': activities  # Pass the activities data to the template
    }

    # Render the template with the summary data
    return summary_dict


if __name__ == '__main__':
    app.run(debug=True)
