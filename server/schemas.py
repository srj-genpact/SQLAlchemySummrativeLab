from marshmallow import Schema, fields, validate, validates, ValidationError

class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, error="Exercise name cannot be empty."))
    category = fields.Str(required=True, validate=validate.OneOf(
        ["Strength", "Cardio", "Flexibility", "Balance"],
        error="Category must be one of: Strength, Cardio, Flexibility, Balance."
    ))
    equipment_needed = fields.Bool(load_default=False)

    class Meta:
        ordered = True


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(required=True)
    exercise_id = fields.Int(required=True)
    reps = fields.Int(required=True, validate=validate.Range(min=1, error="Reps must be at least 1."))
    sets = fields.Int(required=True, validate=validate.Range(min=1, error="Sets must be at least 1."))
    duration_seconds = fields.Int(required=True, validate=validate.Range(min=1, error="Duration seconds must be at least 1."))
    
    # Nested field to return exercise details in workout serializers
    exercise = fields.Nested(ExerciseSchema, dump_only=True)

    class Meta:
        ordered = True


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True, error_messages={"required": "Date is required."})
    duration_minutes = fields.Int(required=True, validate=validate.Range(min=1, error="Duration must be a positive integer."))
    notes = fields.Str(allow_none=True)

    # Nested field to return associated exercises in workout details
    workout_exercises = fields.Nested(WorkoutExerciseSchema, many=True, dump_only=True)

    class Meta:
        ordered = True


class WorkoutExerciseWithWorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    reps = fields.Int(dump_only=True)
    sets = fields.Int(dump_only=True)
    duration_seconds = fields.Int(dump_only=True)
    workout = fields.Nested(WorkoutSchema, exclude=('workout_exercises',), dump_only=True)

    class Meta:
        ordered = True


class ExerciseDetailSchema(ExerciseSchema):
    # Includes workouts associated with the exercise
    workout_exercises = fields.Nested(WorkoutExerciseWithWorkoutSchema, many=True, dump_only=True)

    class Meta:
        ordered = True
