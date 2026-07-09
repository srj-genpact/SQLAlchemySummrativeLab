# Flask SQLAlchemy Workout Application Backend

A complete backend API for a workout tracking application used by personal trainers. Built with Flask, SQLAlchemy, and Marshmallow.

This application manages workouts, exercises, and their associative data (reps, sets, and duration) using SQLite. It implements robust check/unique constraints, model validations, and serialization schema validation rules.

## Tools & Libraries Used
- **Python** (version 3.12.10)
- **Pipenv** for package and environment management
- **Flask** (2.2.2) & **Flask-Migrate** (3.1.0)
- **Flask-SQLAlchemy** (3.0.3)
- **Marshmallow** (3.20.1) for serialization/deserialization & schema validation

---

## Getting Started

### 1. Installation
Clone the repository and install the dependencies into the virtual environment using `pipenv`:
```bash
pipenv install
```

### 2. Database Migrations
Initialize, generate, and run the database migrations:
```bash
# Initialize migrations directory (already initialized in repo)
pipenv run flask --app server/app.py db init

# Generate migration scripts
pipenv run flask --app server/app.py db migrate -m "create tables"

# Apply migration scripts to generate database tables
pipenv run flask --app server/app.py db upgrade
```

### 3. Seeding the Database
Run the seed script to populate the tables with initial workout and exercise data:
```bash
pipenv run python server/seed.py
```

### 4. Running the Application
To run the server locally on port `5555`:
```bash
pipenv run python server/app.py
```

### 5. Running the Tests
To run the automated integration test suite:
```bash
pipenv run python server/test_api.py
```

---

## Database Schema

### 1. Workout
- `id` (Integer, Primary Key)
- `date` (Date, Required)
- `duration_minutes` (Integer, Required, Positive)
- `notes` (Text)

### 2. Exercise
- `id` (Integer, Primary Key)
- `name` (String, Required, Unique, Non-empty)
- `category` (String, Required, must be one of: Strength, Cardio, Flexibility, Balance)
- `equipment_needed` (Boolean, Required, defaults to False)

### 3. WorkoutExercise (Join Table)
- `id` (Integer, Primary Key)
- `workout_id` (ForeignKey to Workouts, Required)
- `exercise_id` (ForeignKey to Exercises, Required)
- `reps` (Integer, Required, Positive)
- `sets` (Integer, Required, Positive)
- `duration_seconds` (Integer, Required, Positive)
- *Constraints*: Unique constraint on `(workout_id, exercise_id)`

---

## API Endpoints

### Workouts
- `GET /workouts` - Retrieves all workouts (excluding exercise sub-details).
- `GET /workouts/<id>` - Retrieves a single workout including all nested exercises, reps, sets, and duration info.
- `POST /workouts` - Creates a new workout. Requires JSON payload with `date` (YYYY-MM-DD format) and `duration_minutes`.
- `DELETE /workouts/<id>` - Deletes a workout (and cascade deletes all associated workout exercise entries).

### Exercises
- `GET /exercises` - Retrieves all exercises.
- `GET /exercises/<id>` - Retrieves an exercise by ID and lists all workouts that include this exercise.
- `POST /exercises` - Creates a new exercise. Requires JSON payload with `name` and `category`.
- `DELETE /exercises/<id>` - Deletes an exercise (and cascade deletes all associated workout exercise entries).

### Workout Exercises (Joint Association)
- `POST /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises`
  - Adds an exercise to a workout with specific performance metrics.
  - Requires JSON payload containing: `reps` (positive int), `sets` (positive int), and `duration_seconds` (positive int).
