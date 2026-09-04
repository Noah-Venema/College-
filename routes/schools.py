from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from app import db
from models import School, Matchup, Campus, CreditTransfer

schools_bp = Blueprint("schools", __name__, url_prefix="/schools")


def _campus_notes_by_school(user_id):
    """Maps lowercased school name -> Campus record, for pulling in campus-life notes."""
    return {c.school_name.strip().lower(): c for c in Campus.query.filter_by(user_id=user_id).all()}


@schools_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("School name is required.", "danger")
        else:
            school = School(
                user_id=current_user.id,
                name=name,
                location=request.form.get("location", "").strip(),
                size=request.form.get("size", "").strip(),
                tuition=request.form.get("tuition", "").strip(),
                acceptance_rate=request.form.get("acceptance_rate", "").strip(),
                notes=request.form.get("notes", "").strip(),
                activities_offered=request.form.get("activities_offered", "").strip(),
                religious_affiliation=request.form.get("religious_affiliation", "").strip(),
                athletic_association=request.form.get("athletic_association", "None"),
            )
            db.session.add(school)
            db.session.commit()
            flash("School added.", "success")
        return redirect(url_for("schools.index"))

    all_schools = School.query.filter_by(user_id=current_user.id).order_by(School.name.asc()).all()
    campus_map = _campus_notes_by_school(current_user.id)
    matchups = Matchup.query.filter_by(user_id=current_user.id).order_by(Matchup.created_at.desc()).all()
    credit_transfers = CreditTransfer.query.filter_by(user_id=current_user.id).order_by(
        CreditTransfer.school_name.asc(), CreditTransfer.exam_name.asc()
    ).all()

    return render_template(
        "schools.html",
        schools=all_schools,
        campus_map=campus_map,
        matchups=matchups,
        credit_transfers=credit_transfers,
        exam_types=CreditTransfer.EXAM_TYPES,
        athletic_associations=School.ATHLETIC_ASSOCIATIONS,
    )


@schools_bp.route("/<int:school_id>/edit", methods=["POST"])
@login_required
def edit_school(school_id):
    school = School.query.filter_by(id=school_id, user_id=current_user.id).first_or_404()
    school.name = request.form.get("name", "").strip() or school.name
    school.location = request.form.get("location", "").strip()
    school.size = request.form.get("size", "").strip()
    school.tuition = request.form.get("tuition", "").strip()
    school.acceptance_rate = request.form.get("acceptance_rate", "").strip()
    school.notes = request.form.get("notes", "").strip()
    school.activities_offered = request.form.get("activities_offered", "").strip()
    school.religious_affiliation = request.form.get("religious_affiliation", "").strip()
    school.athletic_association = request.form.get("athletic_association", school.athletic_association)
    db.session.commit()
    flash("School updated.", "success")
    return redirect(url_for("schools.index"))


@schools_bp.route("/<int:school_id>/delete", methods=["POST"])
@login_required
def delete_school(school_id):
    school = School.query.filter_by(id=school_id, user_id=current_user.id).first_or_404()
    # Remove any matchups referencing this school first to avoid orphaned rows.
    Matchup.query.filter(
        (Matchup.school_a_id == school_id) | (Matchup.school_b_id == school_id),
        Matchup.user_id == current_user.id,
    ).delete()
    db.session.delete(school)
    db.session.commit()
    flash("School deleted.", "info")
    return redirect(url_for("schools.index"))


@schools_bp.route("/matchups", methods=["POST"])
@login_required
def add_matchup():
    school_a_id = request.form.get("school_a_id")
    school_b_id = request.form.get("school_b_id")

    if not school_a_id or not school_b_id:
        flash("Please choose two schools to compare.", "danger")
    elif school_a_id == school_b_id:
        flash("Please choose two different schools.", "danger")
    else:
        matchup = Matchup(
            user_id=current_user.id,
            school_a_id=school_a_id,
            school_b_id=school_b_id,
            notes=request.form.get("notes", "").strip(),
        )
        db.session.add(matchup)
        db.session.commit()
        flash("Matchup added.", "success")

    return redirect(url_for("schools.index"))


@schools_bp.route("/matchups/<int:matchup_id>/delete", methods=["POST"])
@login_required
def delete_matchup(matchup_id):
    matchup = Matchup.query.filter_by(id=matchup_id, user_id=current_user.id).first_or_404()
    db.session.delete(matchup)
    db.session.commit()
    flash("Matchup deleted.", "info")
    return redirect(url_for("schools.index"))


@schools_bp.route("/credit-transfers", methods=["POST"])
@login_required
def add_credit_transfer():
    school_name = request.form.get("school_name", "").strip()
    exam_name = request.form.get("exam_name", "").strip()
    score = request.form.get("score", "").strip()

    if not school_name or not exam_name or not score:
        flash("School, exam name, and score are required.", "danger")
    else:
        entry = CreditTransfer(
            user_id=current_user.id,
            school_name=school_name,
            exam_type=request.form.get("exam_type", "AP"),
            exam_name=exam_name,
            score=score,
            credits_awarded=request.form.get("credits_awarded", "").strip(),
            course_equivalent=request.form.get("course_equivalent", "").strip(),
            policy_link=request.form.get("policy_link", "").strip(),
            notes=request.form.get("notes", "").strip(),
        )
        db.session.add(entry)
        db.session.commit()
        flash("Credit transfer entry added.", "success")

    return redirect(url_for("schools.index"))


@schools_bp.route("/credit-transfers/<int:entry_id>/edit", methods=["POST"])
@login_required
def edit_credit_transfer(entry_id):
    entry = CreditTransfer.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    entry.school_name = request.form.get("school_name", "").strip() or entry.school_name
    entry.exam_type = request.form.get("exam_type", entry.exam_type)
    entry.exam_name = request.form.get("exam_name", "").strip() or entry.exam_name
    entry.score = request.form.get("score", "").strip() or entry.score
    entry.credits_awarded = request.form.get("credits_awarded", "").strip()
    entry.course_equivalent = request.form.get("course_equivalent", "").strip()
    entry.policy_link = request.form.get("policy_link", "").strip()
    entry.notes = request.form.get("notes", "").strip()
    db.session.commit()
    flash("Credit transfer entry updated.", "success")
    return redirect(url_for("schools.index"))


@schools_bp.route("/credit-transfers/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete_credit_transfer(entry_id):
    entry = CreditTransfer.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash("Credit transfer entry deleted.", "info")
    return redirect(url_for("schools.index"))
