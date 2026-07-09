import os
import sys
import unittest
import json
import datetime

# Adjust path to import app and models from the same directory
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from app import app, db
from models import Exercise, Workout, WorkoutExercise

class WorkoutAPITestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test.db'))
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        self.client = app.test_client()
        
        # Push application context for the duration of the test
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Clean state
        db.session.close()
        db.drop_all()
        db.create_all()
        
        # Seed minimal test data
        self.ex1 = Exercise(name="Pushups", category="Strength", equipment_needed=False)
        self.ex2 = Exercise(name="Running", category="Cardio", equipment_needed=False)
        db.session.add_all([self.ex1, self.ex2])
        
        self.w1 = Workout(date=datetime.date(2026, 7, 1), duration_minutes=45, notes="Morning strength")
        db.session.add(self.w1)
        db.session.commit()
        
        # Keep IDs
        self.ex1_id = self.ex1.id
        self.ex2_id = self.ex2.id
        self.w1_id = self.w1.id

    def tearDown(self):
        # Clean up database session and file
        db.session.rollback()
        db.session.close()
        db.drop_all()
        self.app_context.pop()
        
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                pass

    # ================= WORKOUT TESTS =================

    def test_get_workouts(self):
        res = self.client.get('/workouts')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['notes'], "Morning strength")
        # Ensure workout_exercises is excluded in listing endpoint (lazy/clean)
        self.assertNotIn('workout_exercises', data[0])

    def test_get_workout_by_id(self):
        res = self.client.get(f'/workouts/{self.w1_id}')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['notes'], "Morning strength")
        self.assertIn('workout_exercises', data)

    def test_get_workout_not_found(self):
        res = self.client.get('/workouts/999')
        self.assertEqual(res.status_code, 404)
        data = json.loads(res.data)
        self.assertIn('error', data)

    def test_create_workout_success(self):
        payload = {
            "date": "2026-07-04",
            "duration_minutes": 50,
            "notes": "Testing create workout"
        }
        res = self.client.post('/workouts', json=payload)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertIn('id', data)
        self.assertEqual(data['duration_minutes'], 50)

    def test_create_workout_validation_fails(self):
        # 1. Invalid duration (negative)
        payload = {
            "date": "2026-07-04",
            "duration_minutes": -10,
            "notes": "Invalid duration"
        }
        res = self.client.post('/workouts', json=payload)
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertIn('duration_minutes', data)

        # 2. Missing date
        payload = {
            "duration_minutes": 30
        }
        res = self.client.post('/workouts', json=payload)
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertIn('date', data)

    def test_delete_workout(self):
        res = self.client.delete(f'/workouts/{self.w1_id}')
        self.assertEqual(res.status_code, 200)
        
        # Verify it is deleted
        res2 = self.client.get(f'/workouts/{self.w1_id}')
        self.assertEqual(res2.status_code, 404)

    # ================= EXERCISE TESTS =================

    def test_get_exercises(self):
        res = self.client.get('/exercises')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], "Pushups")

    def test_get_exercise_by_id(self):
        res = self.client.get(f'/exercises/{self.ex1_id}')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['name'], "Pushups")
        self.assertIn('workout_exercises', data)

    def test_create_exercise_success(self):
        payload = {
            "name": "Yoga Flex",
            "category": "Flexibility",
            "equipment_needed": False
        }
        res = self.client.post('/exercises', json=payload)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertEqual(data['name'], "Yoga Flex")

    def test_create_exercise_duplicate_name(self):
        payload = {
            "name": "Pushups",
            "category": "Strength"
        }
        res = self.client.post('/exercises', json=payload)
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertIn('error', data)

    def test_create_exercise_invalid_category(self):
        payload = {
            "name": "Bicep Curls",
            "category": "InvalidCategory"
        }
        res = self.client.post('/exercises', json=payload)
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertIn('category', data)

    # ================= JOIN RELATIONSHIP TESTS =================

    def test_add_exercise_to_workout(self):
        payload = {
            "reps": 12,
            "sets": 3,
            "duration_seconds": 90
        }
        res = self.client.post(f'/workouts/{self.w1_id}/exercises/{self.ex1_id}/workout_exercises', json=payload)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertEqual(data['reps'], 12)
        self.assertEqual(data['sets'], 3)
        self.assertEqual(data['workout_id'], self.w1_id)
        self.assertEqual(data['exercise_id'], self.ex1_id)

        # Check duplicate add fails
        res2 = self.client.post(f'/workouts/{self.w1_id}/exercises/{self.ex1_id}/workout_exercises', json=payload)
        self.assertEqual(res2.status_code, 400)
        data2 = json.loads(res2.data)
        self.assertIn('error', data2)

    def test_add_workout_exercise_invalid_data(self):
        # Negative reps
        payload = {
            "reps": -5,
            "sets": 3,
            "duration_seconds": 90
        }
        res = self.client.post(f'/workouts/{self.w1_id}/exercises/{self.ex1_id}/workout_exercises', json=payload)
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertIn('reps', data)

    def test_cascade_delete(self):
        # 1. Add association
        payload = {
            "reps": 10,
            "sets": 3,
            "duration_seconds": 60
        }
        res_post = self.client.post(f'/workouts/{self.w1_id}/exercises/{self.ex1_id}/workout_exercises', json=payload)
        self.assertEqual(res_post.status_code, 201)
        
        # Verify WorkoutExercise exists in DB
        we_count = WorkoutExercise.query.filter_by(workout_id=self.w1_id, exercise_id=self.ex1_id).count()
        self.assertEqual(we_count, 1)

        # 2. Delete Workout
        res_del = self.client.delete(f'/workouts/{self.w1_id}')
        self.assertEqual(res_del.status_code, 200)

        # 3. Verify WorkoutExercise is automatically deleted via cascade
        we_count = WorkoutExercise.query.filter_by(workout_id=self.w1_id, exercise_id=self.ex1_id).count()
        self.assertEqual(we_count, 0)

if __name__ == '__main__':
    unittest.main()
