from datetime import date

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import Essay, Scholarship, FinancialAid, Task, TestEntry, Deadline
from routes.scholarships import _parse_amount, _format_currency

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
    essays = Essay.query.filter_by(user_id=current_user.id).all()
    essay_counts = {status: 0 for status in Essay.STATUSES}
    for e in essays:
        essay_counts[e.status] = essay_counts.get(e.status, 0) + 1

    scholarships = Scholarship.query.filter_by(user_id=current_user.id).all()
    scholarship_counts = {status: 0 for status in Scholarship.STATUSES}
    for s in scholarships:
        scholarship_counts[s.status] = scholarship_counts.get(s.status, 0) + 1
    total_applied = sum(_parse_amount(s.amount) for s in scholarships)
    total_won = sum(_parse_amount(s.amount) for s in scholarships if s.status == "Awarded")

    aid_entries = FinancialAid.query.filter_by(user_id=current_user.id).all()
    aid_counts = {status: 0 for status in FinancialAid.STATUSES}
    for a in aid_entries:
        aid_counts[a.status] = aid_counts.get(a.status, 0) + 1

    tasks = Task.query.filter_by(user_id=current_user.id).all()
    task_counts = {status: 0 for status in Task.STATUSES}
    for t in tasks:
        task_counts[t.status] = task_counts.get(t.status, 0) + 1

    test_count = TestEntry.query.filter_by(user_id=current_user.id).count()

    upcoming_deadlines = (
        Deadline.query.filter(Deadline.user_id == current_user.id, Deadline.date >= date.today())
        .order_by(Deadline.date.asc())
        .limit(5)
        .all()
    )

    return render_template(
        "home.html",
        sections=SECTIONS,
        essay_counts=essay_counts,
        scholarship_counts=scholarship_counts,
        total_applied=_format_currency(total_applied),
        total_won=_format_currency(total_won),
        aid_counts=aid_counts,
        task_counts=task_counts,
        test_count=test_count,
        upcoming_deadlines=upcoming_deadlines,
        today=date.today(),
    )
