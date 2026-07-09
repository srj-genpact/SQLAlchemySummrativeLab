from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import validates
import datetime

metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

db = SQLAlchemy(metadata=metadata)

class Workout(db.Model):
    __tablename__ = 'workouts'
    __table_args__ = (
        CheckConstraint('duration_minutes > 0', name='duration_minutes_positive'),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    # Relationships
    # A Workout has many WorkoutExercises (cascading delete if workout is deleted)
    workout_exercises = db.relationship('WorkoutExercise', back_populates='workout', cascade='all, delete-orphan')
    
    # A Workout has many Exercises through WorkoutExercises
    exercises = db.relationship('Exercise', secondary='workout_exercises', back_populates='workouts', viewonly=True)

    @validates('duration_minutes')
    def validate_duration(self, key, value):
        if value is None:
            raise ValueError("Duration is required.")
        # Ensure it is converted to int if string is passed
        try:
            val_int = int(value)
        except (ValueError, TypeError):
            raise ValueError("Duration must be an integer.")
        if val_int <= 0:
            raise ValueError("Duration must be a positive integer.")
        return val_int

    @validates('date')
    def validate_date(self, key, value):
        if value is None:
            raise ValueError("Date is required.")
        if isinstance(value, str):
            try:
                # Try parsing standard YYYY-MM-DD
                value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format.")
        elif isinstance(value, datetime.datetime):
            value = value.date()
        return value


class Exercise(db.Model):
    __tablename__ = 'exercises'
    __table_args__ = (
        CheckConstraint("name != ''", name='name_not_empty'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    # An Exercise has many WorkoutExercises (cascading delete if exercise is deleted)
    workout_exercises = db.relationship('WorkoutExercise', back_populates='exercise', cascade='all, delete-orphan')

    # An Exercise has many Workouts through WorkoutExercises
    workouts = db.relationship('Workout', secondary='workout_exercises', back_populates='exercises', viewonly=True)

    @validates('name')
    def validate_name(self, key, value):
        if not value or not str(value).strip():
            raise ValueError("Exercise name cannot be empty.")
        return value.strip()

    @validates('category')
    def validate_category(self, key, value):
        valid_categories = ["Strength", "Cardio", "Flexibility", "Balance"]
        if value not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return value


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'
    __table_args__ = (
        UniqueConstraint('workout_id', 'exercise_id', name='uq_workout_exercise'),
        CheckConstraint('reps > 0', name='reps_positive'),
        CheckConstraint('sets > 0', name='sets_positive'),
        CheckConstraint('duration_seconds > 0', name='duration_seconds_positive'),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=False)

    # Relationships
    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    @validates('reps', 'sets', 'duration_seconds')
    def validate_positive_values(self, key, value):
        if value is None:
            raise ValueError(f"{key.capitalize()} is required.")
        try:
            val_int = int(value)
        except (ValueError, TypeError):
            raise ValueError(f"{key.capitalize()} must be an integer.")
        if val_int <= 0:
            raise ValueError(f"{key.capitalize()} must be a positive integer.")
        return val_int
