import os
import uuid
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, send_from_directory, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from models import Essay, Honor, Activity, SchoolProfile, Course, TestEntry, Recommender, User

applications_bp = Blueprint("applications", __name__, url_prefix="/applications")

# Sub-tabs shown across every page in the Applications section.
APP_TABS = [
    {"name": "Essays", "endpoint": "applications.essays"},
    {"name": "Honors & Awards", "endpoint": "applications.honors"},
    {"name": "Activities", "endpoint": "applications.activities"},
    {"name": "School Information", "endpoint": "applications.school_info"},
    {"name": "Testing", "endpoint": "applications.testing"},
    {"name": "Recommenders", "endpoint": "applications.recommenders"},
]


@applications_bp.route("/")
@login_required
def index():
    return redirect(url_for("applications.essays"))


@applications_bp.route("/essays", methods=["GET", "POST"])
@login_required
def essays():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Title is required.", "danger")
        else:
            essay = Essay(
                user_id=current_user.id,
                title=title,
                prompt=request.form.get("prompt", "").strip(),
                school_name=request.form.get("school_name", "").strip(),
                status=request.form.get("status", "Not Started"),
                notes=request.form.get("notes", "").strip(),
            )
            db.session.add(essay)
            db.session.commit()
            flash("Essay added.", "success")
        return redirect(url_for("applications.essays"))

    all_essays = Essay.query.filter_by(user_id=current_user.id).order_by(Essay.updated_at.desc()).all()
    return render_template(
        "applications/essays.html",
        tabs=APP_TABS,
        active_tab="Essays",
        essays=all_essays,
        statuses=Essay.STATUSES,
    )


@applications_bp.route("/essays/<int:essay_id>/edit", methods=["POST"])
@login_required
def edit_essay(essay_id):
    essay = Essay.query.filter_by(id=essay_id, user_id=current_user.id).first_or_404()
    essay.title = request.form.get("title", "").strip() or essay.title
    essay.prompt = request.form.get("prompt", "").strip()
    essay.school_name = request.form.get("school_name", "").strip()
    essay.status = request.form.get("status", essay.status)
    essay.notes = request.form.get("notes", "").strip()
    db.session.commit()
    flash("Essay updated.", "success")
    return redirect(url_for("applications.essays"))


@applications_bp.route("/essays/<int:essay_id>/delete", methods=["POST"])
@login_required
def delete_essay(essay_id):
    essay = Essay.query.filter_by(id=essay_id, user_id=current_user.id).first_or_404()
    db.session.delete(essay)
    db.session.commit()
    flash("Essay deleted.", "info")
    return redirect(url_for("applications.essays"))


# Placeholders for the remaining sub-tabs — built out on their own branches next.
@applications_bp.route("/honors", methods=["GET", "POST"])
@login_required
def honors():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Title is required.", "danger")
        else:
            honor = Honor(
                user_id=current_user.id,
                title=title,
                level=request.form.get("level", "School"),
                date_received=request.form.get("date_received", "").strip(),
                description=request.form.get("description", "").strip(),
            )
            db.session.add(honor)
            db.session.commit()
            flash("Honor/Award added.", "success")
        return redirect(url_for("applications.honors"))

    all_honors = Honor.query.filter_by(user_id=current_user.id).order_by(Honor.updated_at.desc()).all()
    return render_template(
        "applications/honors.html",
        tabs=APP_TABS,
        active_tab="Honors & Awards",
        honors=all_honors,
        levels=Honor.LEVELS,
    )


@applications_bp.route("/honors/<int:honor_id>/edit", methods=["POST"])
@login_required
def edit_honor(honor_id):
    honor = Honor.query.filter_by(id=honor_id, user_id=current_user.id).first_or_404()
    honor.title = request.form.get("title", "").strip() or honor.title
    honor.level = request.form.get("level", honor.level)
    honor.date_received = request.form.get("date_received", "").strip()
    honor.description = request.form.get("description", "").strip()
    db.session.commit()
    flash("Honor/Award updated.", "success")
    return redirect(url_for("applications.honors"))


@applications_bp.route("/honors/<int:honor_id>/delete", methods=["POST"])
@login_required
def delete_honor(honor_id):
    honor = Honor.query.filter_by(id=honor_id, user_id=current_user.id).first_or_404()
    db.session.delete(honor)
    db.session.commit()
    flash("Honor/Award deleted.", "info")
    return redirect(url_for("applications.honors"))


@applications_bp.route("/activities", methods=["GET", "POST"])
@login_required
def activities():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Title is required.", "danger")
        else:
            activity = Activity(
                user_id=current_user.id,
                title=title,
                level=request.form.get("level", "School"),
                years_participated=request.form.get("years_participated", "").strip(),
                description=request.form.get("description", "").strip(),
            )
            db.session.add(activity)
            db.session.commit()
            flash("Activity added.", "success")
        return redirect(url_for("applications.activities"))

    all_activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.updated_at.desc()).all()
    return render_template(
        "applications/activities.html",
        tabs=APP_TABS,
        active_tab="Activities",
        activities=all_activities,
        levels=Activity.LEVELS,
    )


@applications_bp.route("/activities/<int:activity_id>/edit", methods=["POST"])
@login_required
def edit_activity(activity_id):
    activity = Activity.query.filter_by(id=activity_id, user_id=current_user.id).first_or_404()
    activity.title = request.form.get("title", "").strip() or activity.title
    activity.level = request.form.get("level", activity.level)
    activity.years_participated = request.form.get("years_participated", "").strip()
    activity.description = request.form.get("description", "").strip()
    db.session.commit()
    flash("Activity updated.", "success")
    return redirect(url_for("applications.activities"))


@applications_bp.route("/activities/<int:activity_id>/delete", methods=["POST"])
@login_required
def delete_activity(activity_id):
    activity = Activity.query.filter_by(id=activity_id, user_id=current_user.id).first_or_404()
    db.session.delete(activity)
    db.session.commit()
    flash("Activity deleted.", "info")
    return redirect(url_for("applications.activities"))


@applications_bp.route("/school-info", methods=["GET", "POST"])
@login_required
def school_info():
    profile = SchoolProfile.query.filter_by(user_id=current_user.id).first()
    if profile is None:
        profile = SchoolProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()

    if request.method == "POST":
        profile.high_school_name = request.form.get("high_school_name", "").strip()
        profile.gpa = request.form.get("gpa", "").strip()
        profile.class_size = request.form.get("class_size", "").strip()
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("applications.school_info"))

    all_courses = Course.query.filter_by(user_id=current_user.id).order_by(Course.updated_at.desc()).all()
    return render_template(
        "applications/school_info.html",
        tabs=APP_TABS,
        active_tab="School Information",
        profile=profile,
        courses=all_courses,
        levels=Course.LEVELS,
    )


@applications_bp.route("/school-info/courses", methods=["POST"])
@login_required
def add_course():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Course name is required.", "danger")
    else:
        course = Course(
            user_id=current_user.id,
            name=name,
            grade=request.form.get("grade", "").strip(),
            term=request.form.get("term", "").strip(),
            level=request.form.get("level", "Regular"),
        )
        db.session.add(course)
        db.session.commit()
        flash("Course added.", "success")
    return redirect(url_for("applications.school_info"))


@applications_bp.route("/school-info/courses/<int:course_id>/edit", methods=["POST"])
@login_required
def edit_course(course_id):
    course = Course.query.filter_by(id=course_id, user_id=current_user.id).first_or_404()
    course.name = request.form.get("name", "").strip() or course.name
    course.grade = request.form.get("grade", "").strip()
    course.term = request.form.get("term", "").strip()
    course.level = request.form.get("level", course.level)
    db.session.commit()
    flash("Course updated.", "success")
    return redirect(url_for("applications.school_info"))


@applications_bp.route("/school-info/courses/<int:course_id>/delete", methods=["POST"])
@login_required
def delete_course(course_id):
    course = Course.query.filter_by(id=course_id, user_id=current_user.id).first_or_404()
    db.session.delete(course)
    db.session.commit()
    flash("Course deleted.", "info")
    return redirect(url_for("applications.school_info"))


def _allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_UPLOAD_EXTENSIONS"]


def _save_upload(file_storage):
    """Saves an uploaded proof file with a unique name; returns (stored_path, original_name) or (None, None)."""
    if not file_storage or not file_storage.filename:
        return None, None
    if not _allowed_file(file_storage.filename):
        flash("Unsupported file type. Allowed: png, jpg, jpeg, gif, pdf, heic.", "danger")
        return None, None

    original_name = secure_filename(file_storage.filename)
    ext = original_name.rsplit(".", 1)[-1].lower()
    stored_name = f"{uuid.uuid4().hex}.{ext}"
    file_storage.save(os.path.join(current_app.config["UPLOAD_FOLDER"], stored_name))
    return stored_name, original_name


@applications_bp.route("/testing", methods=["GET", "POST"])
@login_required
def testing():
    if request.method == "POST":
        test_name = request.form.get("test_name", "").strip()
        if not test_name:
            flash("Test name is required.", "danger")
        else:
            stored_name, original_name = _save_upload(request.files.get("proof_file"))
            entry = TestEntry(
                user_id=current_user.id,
                test_name=test_name,
                date_taken=request.form.get("date_taken", "").strip(),
                score=request.form.get("score", "").strip(),
                notes=request.form.get("notes", "").strip(),
                file_path=stored_name,
                original_filename=original_name,
            )
            db.session.add(entry)
            db.session.commit()
            flash("Test entry added.", "success")
        return redirect(url_for("applications.testing"))

    all_tests = TestEntry.query.filter_by(user_id=current_user.id).order_by(TestEntry.updated_at.desc()).all()
    return render_template(
        "applications/testing.html",
        tabs=APP_TABS,
        active_tab="Testing",
        tests=all_tests,
    )


@applications_bp.route("/testing/<int:test_id>/edit", methods=["POST"])
@login_required
def edit_test(test_id):
    entry = TestEntry.query.filter_by(id=test_id, user_id=current_user.id).first_or_404()
    entry.test_name = request.form.get("test_name", "").strip() or entry.test_name
    entry.date_taken = request.form.get("date_taken", "").strip()
    entry.score = request.form.get("score", "").strip()
    entry.notes = request.form.get("notes", "").strip()

    stored_name, original_name = _save_upload(request.files.get("proof_file"))
    if stored_name:
        # Remove the old file so uploads don't pile up when replaced.
        if entry.file_path:
            old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], entry.file_path)
            if os.path.exists(old_path):
                os.remove(old_path)
        entry.file_path = stored_name
        entry.original_filename = original_name

    db.session.commit()
    flash("Test entry updated.", "success")
    return redirect(url_for("applications.testing"))


@applications_bp.route("/testing/<int:test_id>/delete", methods=["POST"])
@login_required
def delete_test(test_id):
    entry = TestEntry.query.filter_by(id=test_id, user_id=current_user.id).first_or_404()
    if entry.file_path:
        old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], entry.file_path)
        if os.path.exists(old_path):
            os.remove(old_path)
    db.session.delete(entry)
    db.session.commit()
    flash("Test entry deleted.", "info")
    return redirect(url_for("applications.testing"))


@applications_bp.route("/testing/proof/<path:filename>")
@login_required
def test_proof(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@applications_bp.route("/recommenders", methods=["GET", "POST"])
@login_required
def recommenders():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Recommender name is required.", "danger")
        else:
            recommender = Recommender(
                user_id=current_user.id,
                name=name,
                email=request.form.get("email", "").strip(),
                role=request.form.get("role", "Teacher"),
                school_name=request.form.get("school_name", "").strip(),
                notes=request.form.get("notes", "").strip(),
            )
            db.session.add(recommender)
            db.session.commit()
            flash("Recommender added. Share their portal link to collect the letter.", "success")
        return redirect(url_for("applications.recommenders"))

    all_recommenders = Recommender.query.filter_by(user_id=current_user.id).order_by(
        Recommender.updated_at.desc()
    ).all()
    portal_links = {
        r.id: url_for("applications.recommender_portal", token=r.token, _external=True)
        for r in all_recommenders
    }
    return render_template(
        "applications/recommenders.html",
        tabs=APP_TABS,
        active_tab="Recommenders",
        recommenders=all_recommenders,
        roles=Recommender.ROLES,
        portal_links=portal_links,
    )


@applications_bp.route("/recommenders/<int:recommender_id>/edit", methods=["POST"])
@login_required
def edit_recommender(recommender_id):
    recommender = Recommender.query.filter_by(id=recommender_id, user_id=current_user.id).first_or_404()
    recommender.name = request.form.get("name", "").strip() or recommender.name
    recommender.email = request.form.get("email", "").strip()
    recommender.role = request.form.get("role", recommender.role)
    recommender.school_name = request.form.get("school_name", "").strip()
    recommender.notes = request.form.get("notes", "").strip()
    db.session.commit()
    flash("Recommender updated.", "success")
    return redirect(url_for("applications.recommenders"))


@applications_bp.route("/recommenders/<int:recommender_id>/remind", methods=["POST"])
@login_required
def remind_recommender(recommender_id):
    """Resets the requested_at timestamp to log that a fresh reminder was sent."""
    recommender = Recommender.query.filter_by(id=recommender_id, user_id=current_user.id).first_or_404()
    recommender.requested_at = datetime.utcnow()
    db.session.commit()
    flash(f"Reminder logged for {recommender.name}.", "success")
    return redirect(url_for("applications.recommenders"))


@applications_bp.route("/recommenders/<int:recommender_id>/delete", methods=["POST"])
@login_required
def delete_recommender(recommender_id):
    recommender = Recommender.query.filter_by(id=recommender_id, user_id=current_user.id).first_or_404()
    if recommender.letter_path:
        old_path = os.path.join(current_app.config["RECOMMENDER_UPLOAD_FOLDER"], recommender.letter_path)
        if os.path.exists(old_path):
            os.remove(old_path)
    db.session.delete(recommender)
    db.session.commit()
    flash("Recommender removed.", "info")
    return redirect(url_for("applications.recommenders"))


def _save_recommender_upload(file_storage):
    """Saves an uploaded recommendation letter with a unique name; returns (stored_path, original_name)."""
    if not file_storage or not file_storage.filename:
        return None, None
    if not _allowed_file(file_storage.filename):
        flash("Unsupported file type. Allowed: png, jpg, jpeg, gif, pdf, heic.", "danger")
        return None, None

    original_name = secure_filename(file_storage.filename)
    ext = original_name.rsplit(".", 1)[-1].lower()
    stored_name = f"{uuid.uuid4().hex}.{ext}"
    file_storage.save(os.path.join(current_app.config["RECOMMENDER_UPLOAD_FOLDER"], stored_name))
    return stored_name, original_name


@applications_bp.route("/recommenders/portal/<token>", methods=["GET", "POST"])
def recommender_portal(token):
    """Public, login-free page a recommender can use to upload their letter.

    Authenticated by an unguessable per-recommender token instead of a session,
    since the recommender doesn't (and shouldn't need to) have an account here.
    """
    recommender = Recommender.query.filter_by(token=token).first()
    if recommender is None:
        abort(404)

    student = User.query.get(recommender.user_id)

    if request.method == "POST":
        stored_name, original_name = _save_recommender_upload(request.files.get("letter_file"))
        if stored_name:
            if recommender.letter_path:
                old_path = os.path.join(current_app.config["RECOMMENDER_UPLOAD_FOLDER"], recommender.letter_path)
                if os.path.exists(old_path):
                    os.remove(old_path)
            recommender.letter_path = stored_name
            recommender.letter_original_filename = original_name
            recommender.status = "Received"
            recommender.received_at = datetime.utcnow()
            db.session.commit()
            flash("Thank you! Your letter has been submitted.", "success")
        return redirect(url_for("applications.recommender_portal", token=token))

    return render_template(
        "applications/recommender_portal.html",
        recommender=recommender,
        student=student,
    )


@applications_bp.route("/recommenders/letter/<path:filename>")
@login_required
def recommender_letter(filename):
    recommender = Recommender.query.filter_by(letter_path=filename, user_id=current_user.id).first_or_404()
    return send_from_directory(current_app.config["RECOMMENDER_UPLOAD_FOLDER"], filename)
