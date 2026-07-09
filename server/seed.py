#!/usr/bin/env python3
import os
import sys
import datetime

# Adjust path to allow importing app and models from the same directory
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from app import app
from models import db, Exercise, Workout, WorkoutExercise

def seed_database():
    print("Starting database seed...")
    with app.app_context():
        # Clear existing tables
        print("Clearing existing data...")
        db.session.query(WorkoutExercise).delete()
        db.session.query(Workout).delete()
        db.session.query(Exercise).delete()
        db.session.commit()

        # Seed Exercises
        print("Seeding exercises...")
        pushups = Exercise(name="Pushups", category="Strength", equipment_needed=False)
        squats = Exercise(name="Squats", category="Strength", equipment_needed=False)
        running = Exercise(name="Running", category="Cardio", equipment_needed=False)
        yoga = Exercise(name="Yoga", category="Flexibility", equipment_needed=False)
        bicep_curls = Exercise(name="Bicep Curls", category="Strength", equipment_needed=True)
        plank = Exercise(name="Plank", category="Strength", equipment_needed=False)
        
        db.session.add_all([pushups, squats, running, yoga, bicep_curls, plank])
        db.session.commit()

        # Seed Workouts
        print("Seeding workouts...")
        w1 = Workout(
            date=datetime.date(2026, 7, 1),
            duration_minutes=45,
            notes="Morning strength session"
        )
        w2 = Workout(
            date=datetime.date(2026, 7, 2),
            duration_minutes=30,
            notes="Evening cardio session"
        )
        w3 = Workout(
            date=datetime.date(2026, 7, 3),
            duration_minutes=60,
            notes="Yoga and core flexibility"
        )
        
        db.session.add_all([w1, w2, w3])
        db.session.commit()

        # Seed Workout Exercises
        print("Seeding workout exercises (relationships)...")
        # Workout 1 exercises
        we1 = WorkoutExercise(workout=w1, exercise=pushups, reps=15, sets=3, duration_seconds=180)
        we2 = WorkoutExercise(workout=w1, exercise=squats, reps=20, sets=3, duration_seconds=240)
        
        # Workout 2 exercises
        we3 = WorkoutExercise(workout=w2, exercise=running, reps=1, sets=1, duration_seconds=1800)
        
        # Workout 3 exercises
        we4 = WorkoutExercise(workout=w3, exercise=yoga, reps=10, sets=2, duration_seconds=1200)
        we5 = WorkoutExercise(workout=w3, exercise=plank, reps=3, sets=3, duration_seconds=180)
        
        db.session.add_all([we1, we2, we3, we4, we5])
        db.session.commit()
        
        print("Database successfully seeded!")

if __name__ == '__main__':
    seed_database()
