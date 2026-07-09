import os
import sys
from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

# Adjust path to allow importing models and schemas from the same directory
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from models import db, Exercise, Workout, WorkoutExercise
from schemas import (
    ExerciseSchema,
    WorkoutSchema,
    WorkoutExerciseSchema,
    ExerciseDetailSchema
)

app = Flask(__name__)
# Ensure the database is saved in the server directory
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)

# Instantiate schemas
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
exercise_detail_schema = ExerciseDetailSchema()

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True, exclude=('workout_exercises',))

workout_exercise_schema = WorkoutExerciseSchema()

@app.route('/')
def index():
    return jsonify({"message": "Workout Application API"}), 200

# ================= WORKOUT ENDPOINTS =================

@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.all()
    return make_response(jsonify(workouts_schema.dump(workouts)), 200)

@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout_by_id(id):
    workout = Workout.query.get(id)
    if not workout:
        return make_response(jsonify({"error": "Workout not found"}), 404)
    return make_response(jsonify(workout_schema.dump(workout)), 200)

@app.route('/workouts', methods=['POST'])
def create_workout():
    json_data = request.get_json()
    if not json_data:
        return make_response(jsonify({"error": "No input data provided"}), 400)
    
    try:
        # Load and validate input data
        data = workout_schema.load(json_data)
    except ValidationError as err:
        return make_response(jsonify(err.messages), 400)
    
    try:
        new_workout = Workout(
            date=data['date'],
            duration_minutes=data['duration_minutes'],
            notes=data.get('notes')
        )
        db.session.add(new_workout)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({"error": str(e)}), 400)
        
    return make_response(jsonify(workout_schema.dump(new_workout)), 201)

@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = Workout.query.get(id)
    if not workout:
        return make_response(jsonify({"error": "Workout not found"}), 404)
    
    try:
        db.session.delete(workout)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({"error": str(e)}), 400)
        
    return make_response(jsonify({"message": "Workout successfully deleted"}), 200)

# ================= EXERCISE ENDPOINTS =================

@app.route('/exercises', methods=['GET'])
def get_exercises():
    exercises = Exercise.query.all()
    return make_response(jsonify(exercises_schema.dump(exercises)), 200)

@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise_by_id(id):
    exercise = Exercise.query.get(id)
    if not exercise:
        return make_response(jsonify({"error": "Exercise not found"}), 404)
    return make_response(jsonify(exercise_detail_schema.dump(exercise)), 200)

@app.route('/exercises', methods=['POST'])
def create_exercise():
    json_data = request.get_json()
    if not json_data:
        return make_response(jsonify({"error": "No input data provided"}), 400)
    
    try:
        data = exercise_schema.load(json_data)
    except ValidationError as err:
        return make_response(jsonify(err.messages), 400)
        
    try:
        new_exercise = Exercise(
            name=data['name'],
            category=data['category'],
            equipment_needed=data.get('equipment_needed', False)
        )
        db.session.add(new_exercise)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return make_response(jsonify({"error": "Exercise name already exists"}), 400)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({"error": str(e)}), 400)
        
    return make_response(jsonify(exercise_schema.dump(new_exercise)), 201)

@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    exercise = Exercise.query.get(id)
    if not exercise:
        return make_response(jsonify({"error": "Exercise not found"}), 404)
        
    try:
        db.session.delete(exercise)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({"error": str(e)}), 400)
        
    return make_response(jsonify({"message": "Exercise successfully deleted"}), 200)

# ================= WORKOUT-EXERCISE JOIN ENDPOINT =================

@app.route('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises', methods=['POST'])
def add_workout_exercise(workout_id, exercise_id):
    # Verify workout exists
    workout = Workout.query.get(workout_id)
    if not workout:
        return make_response(jsonify({"error": "Workout not found"}), 404)
        
    # Verify exercise exists
    exercise = Exercise.query.get(exercise_id)
    if not exercise:
        return make_response(jsonify({"error": "Exercise not found"}), 404)
        
    json_data = request.get_json() or {}
    # Inject IDs from URL parameters
    json_data['workout_id'] = workout_id
    json_data['exercise_id'] = exercise_id
    
    try:
        data = workout_exercise_schema.load(json_data)
    except ValidationError as err:
        return make_response(jsonify(err.messages), 400)
        
    # Check if workout-exercise association already exists
    existing = WorkoutExercise.query.filter_by(workout_id=workout_id, exercise_id=exercise_id).first()
    if existing:
        return make_response(jsonify({"error": "Exercise is already added to this workout"}), 400)
        
    try:
        new_we = WorkoutExercise(
            workout_id=workout_id,
            exercise_id=exercise_id,
            reps=data['reps'],
            sets=data['sets'],
            duration_seconds=data['duration_seconds']
        )
        db.session.add(new_we)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return make_response(jsonify({"error": "Could not associate exercise with workout due to data constraints"}), 400)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({"error": str(e)}), 400)
        
    return make_response(jsonify(workout_exercise_schema.dump(new_we)), 201)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
