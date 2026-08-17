from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint("main", __name__)

# Sections shown as tiles on the home dashboard and in the navbar.
SECTIONS = [
    {"name": "Scholarships", "endpoint": "main.scholarships", "icon": "bi-award", "desc": "Track scholarship opportunities, deadlines, and status."},
    {"name": "Financial Aid", "endpoint": "main.financial_aid", "icon": "bi-cash-coin", "desc": "FAFSA, grants, loans, and award letters in one place."},
    {"name": "Applications", "endpoint": "applications.index", "icon": "bi-file-earmark-text", "desc": "Essays, honors, awards, and application progress."},
    {"name": "School Comparison", "endpoint": "main.schools", "icon": "bi-bank", "desc": "Compare schools side by side."},
    {"name": "Housing", "endpoint": "main.housing", "icon": "bi-house-door", "desc": "Dorms, off-campus options, and housing notes."},
    {"name": "Contacts", "endpoint": "main.contacts", "icon": "bi-person-lines-fill", "desc": "Admissions reps, counselors, and other contacts."},
    {"name": "Notes", "endpoint": "notes.board", "icon": "bi-journal-text", "desc": "General notes and reminders."},
]


@main_bp.route("/")
@login_required
def home():
    return render_template("home.html", sections=SECTIONS)


# Placeholder routes for each section — real functionality is built out on
# feature branches one at a time. These exist now so links never 404.
@main_bp.route("/scholarships")
@login_required
def scholarships():
    return render_template("placeholder.html", title="Scholarships")


@main_bp.route("/financial-aid")
@login_required
def financial_aid():
    return render_template("placeholder.html", title="Financial Aid")


@main_bp.route("/schools")
@login_required
def schools():
    return render_template("placeholder.html", title="School Comparison")


@main_bp.route("/housing")
@login_required
def housing():
    return render_template("placeholder.html", title="Housing")


@main_bp.route("/contacts")
@login_required
def contacts():
    return render_template("placeholder.html", title="Contacts")
