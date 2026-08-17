from datetime import datetime
import uuid

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # Unguessable token used to authenticate the calendar .ics feed URL,
    # since external calendar apps (Google/Apple) can't send a login session.
    calendar_token = db.Column(db.String(64), unique=True, default=lambda: uuid.uuid4().hex)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Essay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    prompt = db.Column(db.Text)
    school_name = db.Column(db.String(200))
    status = db.Column(db.String(30), nullable=False, default="Not Started")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    STATUSES = ["Not Started", "Draft", "Final", "Submitted"]


class Honor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    level = db.Column(db.String(30), nullable=False, default="School")
    date_received = db.Column(db.String(20))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    LEVELS = ["School", "District", "State", "National"]


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    level = db.Column(db.String(30), nullable=False, default="School")
    years_participated = db.Column(db.String(50))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    LEVELS = ["School", "District", "State", "National"]


class SchoolProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    high_school_name = db.Column(db.String(200))
    gpa = db.Column(db.String(10))
    class_size = db.Column(db.String(20))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    grade = db.Column(db.String(10))
    term = db.Column(db.String(50))
    level = db.Column(db.String(30), nullable=False, default="Regular")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    LEVELS = ["Regular", "Honors", "AP", "Dual Enrollment"]


class TestEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(100), nullable=False)
    date_taken = db.Column(db.String(20))
    score = db.Column(db.String(30))
    notes = db.Column(db.Text)
    file_path = db.Column(db.String(300))
    original_filename = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default="To-Do")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    STATUSES = ["To-Do", "In Progress", "Done"]


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="Other")
    organization = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(30))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ROLES = ["Admissions Rep", "Counselor", "Coach", "Teacher", "Other"]


class Campus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_name = db.Column(db.String(200), nullable=False)
    housing_info = db.Column(db.Text)
    food_info = db.Column(db.Text)
    student_ratio = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200))
    size = db.Column(db.String(50))
    tuition = db.Column(db.String(50))
    acceptance_rate = db.Column(db.String(20))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Matchup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_a_id = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)
    school_b_id = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    school_a = db.relationship("School", foreign_keys=[school_a_id])
    school_b = db.relationship("School", foreign_keys=[school_b_id])


class Scholarship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.String(30))
    deadline = db.Column(db.String(20))
    status = db.Column(db.String(20), nullable=False, default="Not Started")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    STATUSES = ["Not Started", "In Progress", "Submitted", "Awarded", "Rejected"]


class FinancialAid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(30), nullable=False, default="Other")
    name = db.Column(db.String(200))
    amount = db.Column(db.String(30))
    status = db.Column(db.String(20), nullable=False, default="Pending")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    SOURCES = ["FAFSA", "Grant", "Loan", "Work-Study", "Other"]
    STATUSES = ["Pending", "Received", "Denied"]


class Deadline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(30), nullable=False, default="Other")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    CATEGORIES = ["Task", "Scholarship", "Application", "Financial Aid", "Other"]
