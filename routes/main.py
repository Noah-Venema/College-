from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint("main", __name__)

# Sections shown as tiles on the home dashboard and in the navbar.
SECTIONS = [
    {"name": "Scholarships", "endpoint": "scholarships.index", "icon": "bi-award", "desc": "Track scholarship opportunities, deadlines, and status."},
    {"name": "Financial Aid", "endpoint": "financial_aid.index", "icon": "bi-cash-coin", "desc": "FAFSA, grants, loans, and award letters in one place."},
    {"name": "Applications", "endpoint": "applications.index", "icon": "bi-file-earmark-text", "desc": "Essays, honors, awards, and application progress."},
    {"name": "School Comparison", "endpoint": "schools.index", "icon": "bi-bank", "desc": "Compare schools side by side."},
    {"name": "Campus", "endpoint": "campus.index", "icon": "bi-house-door", "desc": "Dorms, food, teacher-to-student ratio, and campus life info."},
    {"name": "Contacts", "endpoint": "contacts.index", "icon": "bi-person-lines-fill", "desc": "Admissions reps, counselors, and other contacts."},
    {"name": "Notes", "endpoint": "notes.board", "icon": "bi-journal-text", "desc": "General notes and reminders."},
    {"name": "Calendar", "endpoint": "calendar.index", "icon": "bi-calendar-event", "desc": "See all your deadlines in one place, syncable with Google/Apple Calendar."},
    {"name": "Community", "endpoint": "community.feed", "icon": "bi-people", "desc": "Discuss your chances, share your school list, and connect with friends."},
]


@main_bp.route("/")
@login_required
def home():
    return render_template("home.html", sections=SECTIONS)
