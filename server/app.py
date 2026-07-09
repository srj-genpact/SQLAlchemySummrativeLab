import os
import sys
from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate

# Adjust path to allow importing models from the same directory
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from models import db, Exercise, Workout, WorkoutExercise

app = Flask(__name__)
# Ensure the database is saved in the server directory
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return jsonify({"message": "Workout Application API"}), 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)
