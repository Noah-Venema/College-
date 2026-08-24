import os
import uuid
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, send_from_directory, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from models import (
    Essay,
    EssayPrompt,
    BrainstormEntry,
    EssayReview,
    Honor,
    Activity,
    SchoolProfile,
    Course,
    TestEntry,
    Recommender,
    User,
)

applications_bp = Blueprint("applications", __name__, url_prefix="/applications")

# Sub-navigation shown across the Essays workspace pages.
ESSAY_TOOL_TABS = [
    {"name": "My Essays", "endpoint": "applications.essays"},
    {"name": "Prompt Bank", "endpoint": "applications.essay_prompts"},
    {"name": "Brainstorming", "endpoint": "applications.essay_brainstorm"},
    {"name": "Why Us Generator", "endpoint": "applications.essay_why_us"},
    {"name": "Peer Review", "endpoint": "applications.essay_peer_review"},
    {"name": "Common Mistakes", "endpoint": "applications.essay_mistakes"},
]

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
            word_limit = request.form.get("word_limit", "").strip()
            essay = Essay(
                user_id=current_user.id,
                title=title,
                prompt=request.form.get("prompt", "").strip(),
                school_name=request.form.get("school_name", "").strip(),
                status=request.form.get("status", "Not Started"),
                essay_type=request.form.get("essay_type", "Personal Statement"),
                word_limit=int(word_limit) if word_limit.isdigit() else None,
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
        essay_tabs=ESSAY_TOOL_TABS,
        active_essay_tab="My Essays",
        essays=all_essays,
        statuses=Essay.STATUSES,
        essay_types=Essay.TYPES,
    )


@applications_bp.route("/essays/<int:essay_id>/edit", methods=["POST"])
@login_required
def edit_essay(essay_id):
    essay = Essay.query.filter_by(id=essay_id, user_id=current_user.id).first_or_404()
    essay.title = request.form.get("title", "").strip() or essay.title
    essay.prompt = request.form.get("prompt", "").strip()
    essay.school_name = request.form.get("school_name", "").strip()
    essay.status = request.form.get("status", essay.status)
    essay.essay_type = request.form.get("essay_type", essay.essay_type)
    word_limit = request.form.get("word_limit", "").strip()
    essay.word_limit = int(word_limit) if word_limit.isdigit() else None
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


@applications_bp.route("/essays/<int:essay_id>/workspace", methods=["GET", "POST"])
@login_required
def essay_workspace(essay_id):
    """The essay editor: draft content, live word/char counter, cliché/tone checker,
    voice-to-text drafting, and the open-for-peer-review toggle all live here."""
    essay = Essay.query.filter_by(id=essay_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        essay.content = request.form.get("content", "")
        essay.is_open_for_review = request.form.get("is_open_for_review") == "on"
        db.session.commit()
        flash("Draft saved.", "success")
        return redirect(url_for("applications.essay_workspace", essay_id=essay.id))

    reviews = EssayReview.query.filter_by(essay_id=essay.id).order_by(EssayReview.created_at.desc()).all()

    return render_template(
        "applications/essay_workspace.html",
        tabs=APP_TABS,
        active_tab="Essays",
        essay_tabs=ESSAY_TOOL_TABS,
        active_essay_tab="My Essays",
        essay=essay,
        reviews=reviews,
    )


@applications_bp.route("/essays/prompts", methods=["GET", "POST"])
@login_required
def essay_prompts():
    """Prompt Repository: built-in Common App/Coalition App prompts (visible to everyone)
    plus each student's own school-specific supplemental prompts."""
    if request.method == "POST":
        prompt_text = request.form.get("prompt_text", "").strip()
        if not prompt_text:
            flash("Prompt text is required.", "danger")
        else:
            word_limit = request.form.get("word_limit", "").strip()
            prompt = EssayPrompt(
                user_id=current_user.id,
                category=request.form.get("category", "Custom"),
                school_name=request.form.get("school_name", "").strip(),
                prompt_text=prompt_text,
                word_limit=int(word_limit) if word_limit.isdigit() else None,
            )
            db.session.add(prompt)
            db.session.commit()
            flash("Prompt added.", "success")
        return redirect(url_for("applications.essay_prompts"))

    search = request.args.get("q", "").strip()
    query = EssayPrompt.query.filter(
        (EssayPrompt.user_id == current_user.id) | (EssayPrompt.user_id.is_(None))
    )
    if search:
        like = f"%{search}%"
        query = query.filter(
            (EssayPrompt.prompt_text.ilike(like)) | (EssayPrompt.school_name.ilike(like))
        )
    all_prompts = query.order_by(EssayPrompt.category.asc(), EssayPrompt.created_at.asc()).all()

    return render_template(
        "applications/essay_prompts.html",
        tabs=APP_TABS,
        active_tab="Essays",
        essay_tabs=ESSAY_TOOL_TABS,
        active_essay_tab="Prompt Bank",
        prompts=all_prompts,
        categories=EssayPrompt.CATEGORIES,
        search=search,
    )


@applications_bp.route("/essays/prompts/<int:prompt_id>/use", methods=["POST"])
@login_required
def use_prompt(prompt_id):
    """Creates a new Essay pre-filled from a prompt bank entry."""
    prompt = EssayPrompt.query.filter(
        EssayPrompt.id == prompt_id,
        (EssayPrompt.user_id == current_user.id) | (EssayPrompt.user_id.is_(None)),
    ).first_or_404()

    essay = Essay(
        user_id=current_user.id,
        title=f"{prompt.category} Essay" + (f" — {prompt.school_name}" if prompt.school_name else ""),
        prompt=prompt.prompt_text,
        school_name=prompt.school_name or "",
        status="Not Started",
        essay_type="Supplemental / Why Us" if prompt.category == "School Supplemental" else "Personal Statement",
        word_limit=prompt.word_limit,
    )
    db.session.add(essay)
    db.session.commit()
    flash("Essay created from prompt — start drafting in My Essays.", "success")
    return redirect(url_for("applications.essay_workspace", essay_id=essay.id))


@applications_bp.route("/essays/prompts/<int:prompt_id>/delete", methods=["POST"])
@login_required
def delete_prompt(prompt_id):
    # Only custom prompts a user added themselves can be deleted — built-ins (user_id=None)
    # are shared reference data.
    prompt = EssayPrompt.query.filter_by(id=prompt_id, user_id=current_user.id).first_or_404()
    db.session.delete(prompt)
    db.session.commit()
    flash("Prompt removed.", "info")
    return redirect(url_for("applications.essay_prompts"))


@applications_bp.route("/essays/brainstorm", methods=["GET", "POST"])
@login_required
def essay_brainstorm():
    """Brainstorming Bootcamp: 5 guided reflective questions to surface topic ideas."""
    if request.method == "POST":
        entry = BrainstormEntry(
            user_id=current_user.id,
            essay_id=request.form.get("essay_id") or None,
            answer_1=request.form.get("answer_1", "").strip(),
            answer_2=request.form.get("answer_2", "").strip(),
            answer_3=request.form.get("answer_3", "").strip(),
            answer_4=request.form.get("answer_4", "").strip(),
            answer_5=request.form.get("answer_5", "").strip(),
        )
        db.session.add(entry)
        db.session.commit()
        flash("Brainstorm saved — look for themes across your answers.", "success")
        return redirect(url_for("applications.essay_brainstorm"))

    past_entries = BrainstormEntry.query.filter_by(user_id=current_user.id).order_by(
        BrainstormEntry.created_at.desc()
    ).all()
    my_essays = Essay.query.filter_by(user_id=current_user.id).order_by(Essay.title.asc()).all()

    return render_template(
        "applications/essay_brainstorm.html",
        tabs=APP_TABS,
        active_tab="Essays",
        essay_tabs=ESSAY_TOOL_TABS,
        active_essay_tab="Brainstorming",
        questions=BrainstormEntry.QUESTIONS,
        past_entries=past_entries,
        my_essays=my_essays,
    )


@applications_bp.route("/essays/brainstorm/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete_brainstorm(entry_id):
    entry = BrainstormEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash("Brainstorm entry deleted.", "info")
    return redirect(url_for("applications.essay_brainstorm"))


@applications_bp.route("/essays/why-us")
@login_required
def essay_why_us():
    """Why-Us Mad Libs: a fill-in-the-blank template highlighting exactly where to
    insert school-specific facts (professors, programs, clubs) — pure client-side tool."""
    return render_template(
        "applications/essay_why_us.html",
        tabs=APP_TABS,
        active_tab="Essays",
        essay_tabs=ESSAY_TOOL_TABS,
        active_essay_tab="Why Us Generator",
    )


@applications_bp.route("/essays/mistakes")
@login_required
def essay_mistakes():
    """Common Mistakes Library: static curated reference content."""
    return render_template(
        "applications/essay_mistakes.html",
        tabs=APP_TABS,
        active_tab="Essays",
        essay_tabs=ESSAY_TOOL_TABS,
        active_essay_tab="Common Mistakes",
    )


@applications_bp.route("/essays/peer-review")
@login_required
def essay_peer_review():
    """Anonymous Peer Review Exchange: browse other students' essays opted into the
    review pool (never your own), leave rubric feedback, and see feedback you've
    received on your own opted-in essays."""
    already_reviewed_ids = {
        r.essay_id
        for r in EssayReview.query.filter_by(reviewer_user_id=current_user.id).all()
    }
    queue = (
        Essay.query.filter(
            Essay.is_open_for_review.is_(True),
            Essay.user_id != current_user.id,
        )
        .order_by(Essay.updated_at.desc())
        .all()
    )
    queue = [e for e in queue if e.id not in already_reviewed_ids]

    my_open_essays = Essay.query.filter_by(user_id=current_user.id, is_open_for_review=True).all()
    feedback_received = {
        essay.id: EssayReview.query.filter_by(essay_id=essay.id).order_by(EssayReview.created_at.desc()).all()
        for essay in my_open_essays
    }

    return render_template(
        "applications/essay_peer_review.html",
        tabs=APP_TABS,
        active_tab="Essays",
        essay_tabs=ESSAY_TOOL_TABS,
        active_essay_tab="Peer Review",
        queue=queue,
        my_open_essays=my_open_essays,
        feedback_received=feedback_received,
    )


@applications_bp.route("/essays/peer-review/<int:essay_id>/submit", methods=["POST"])
@login_required
def submit_essay_review(essay_id):
    essay = Essay.query.filter(
        Essay.id == essay_id,
        Essay.is_open_for_review.is_(True),
        Essay.user_id != current_user.id,
    ).first_or_404()

    existing = EssayReview.query.filter_by(essay_id=essay.id, reviewer_user_id=current_user.id).first()
    if existing:
        flash("You've already reviewed this essay.", "info")
        return redirect(url_for("applications.essay_peer_review"))

    def _rating(field):
        try:
            value = int(request.form.get(field, 0))
        except (TypeError, ValueError):
            value = 0
        return max(1, min(5, value)) if value else 3

    review = EssayReview(
        essay_id=essay.id,
        reviewer_user_id=current_user.id,
        clarity_rating=_rating("clarity_rating"),
        voice_rating=_rating("voice_rating"),
        structure_rating=_rating("structure_rating"),
        comments=request.form.get("comments", "").strip(),
    )
    db.session.add(review)
    db.session.commit()
    flash("Feedback submitted — thanks for helping a fellow applicant!", "success")
    return redirect(url_for("applications.essay_peer_review"))


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
