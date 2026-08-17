from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required

from app import db
from models import School, Matchup, Campus

schools_bp = Blueprint("schools", __name__, url_prefix="/schools")


def _campus_notes_by_school():
    """Maps lowercased school name -> Campus record, for pulling in campus-life notes."""
    return {c.school_name.strip().lower(): c for c in Campus.query.all()}


@schools_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("School name is required.", "danger")
        else:
            school = School(
                name=name,
                location=request.form.get("location", "").strip(),
                size=request.form.get("size", "").strip(),
                tuition=request.form.get("tuition", "").strip(),
                acceptance_rate=request.form.get("acceptance_rate", "").strip(),
                notes=request.form.get("notes", "").strip(),
            )
            db.session.add(school)
            db.session.commit()
            flash("School added.", "success")
        return redirect(url_for("schools.index"))

    all_schools = School.query.order_by(School.name.asc()).all()
    campus_map = _campus_notes_by_school()
    matchups = Matchup.query.order_by(Matchup.created_at.desc()).all()

    return render_template(
        "schools.html",
        schools=all_schools,
        campus_map=campus_map,
        matchups=matchups,
    )


@schools_bp.route("/<int:school_id>/edit", methods=["POST"])
@login_required
def edit_school(school_id):
    school = School.query.get_or_404(school_id)
    school.name = request.form.get("name", "").strip() or school.name
    school.location = request.form.get("location", "").strip()
    school.size = request.form.get("size", "").strip()
    school.tuition = request.form.get("tuition", "").strip()
    school.acceptance_rate = request.form.get("acceptance_rate", "").strip()
    school.notes = request.form.get("notes", "").strip()
    db.session.commit()
    flash("School updated.", "success")
    return redirect(url_for("schools.index"))


@schools_bp.route("/<int:school_id>/delete", methods=["POST"])
@login_required
def delete_school(school_id):
    school = School.query.get_or_404(school_id)
    # Remove any matchups referencing this school first to avoid orphaned rows.
    Matchup.query.filter(
        (Matchup.school_a_id == school_id) | (Matchup.school_b_id == school_id)
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
    matchup = Matchup.query.get_or_404(matchup_id)
    db.session.delete(matchup)
    db.session.commit()
    flash("Matchup deleted.", "info")
    return redirect(url_for("schools.index"))
