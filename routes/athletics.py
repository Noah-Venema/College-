from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from app import db
from models import AthleteProfile, RecruitingEntry, School

athletics_bp = Blueprint("athletics", __name__, url_prefix="/athletics")


@athletics_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    profile = AthleteProfile.query.filter_by(user_id=current_user.id).first()
    if profile is None:
        profile = AthleteProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()

    if request.method == "POST":
        profile.primary_sport = request.form.get("primary_sport", "").strip()
        profile.position = request.form.get("position", "").strip()
        profile.graduation_year = request.form.get("graduation_year", "").strip()
        profile.height = request.form.get("height", "").strip()
        profile.weight = request.form.get("weight", "").strip()
        profile.ncaa_eligibility_status = request.form.get("ncaa_eligibility_status", profile.ncaa_eligibility_status)
        profile.ncaa_id = request.form.get("ncaa_id", "").strip()
        profile.naia_eligibility_status = request.form.get("naia_eligibility_status", profile.naia_eligibility_status)
        profile.naia_id = request.form.get("naia_id", "").strip()
        profile.highlight_video_link = request.form.get("highlight_video_link", "").strip()
        profile.notes = request.form.get("notes", "").strip()
        db.session.commit()
        flash("Athlete profile updated.", "success")
        return redirect(url_for("athletics.index"))

    recruiting_entries = RecruitingEntry.query.filter_by(user_id=current_user.id).order_by(
        RecruitingEntry.updated_at.desc()
    ).all()
    schools = School.query.filter_by(user_id=current_user.id).order_by(School.name.asc()).all()

    return render_template(
        "athletics.html",
        profile=profile,
        recruiting_entries=recruiting_entries,
        schools=schools,
        eligibility_statuses=AthleteProfile.ELIGIBILITY_STATUSES,
        divisions=School.ATHLETIC_ASSOCIATIONS,
        recruiting_statuses=RecruitingEntry.STATUSES,
    )


@athletics_bp.route("/recruiting", methods=["POST"])
@login_required
def add_recruiting_entry():
    school_name = request.form.get("school_name", "").strip()
    if not school_name:
        flash("School name is required.", "danger")
    else:
        entry = RecruitingEntry(
            user_id=current_user.id,
            school_name=school_name,
            division=request.form.get("division", "None"),
            coach_name=request.form.get("coach_name", "").strip(),
            coach_email=request.form.get("coach_email", "").strip(),
            coach_phone=request.form.get("coach_phone", "").strip(),
            status=request.form.get("status", "Not Contacted"),
            scholarship_details=request.form.get("scholarship_details", "").strip(),
            notes=request.form.get("notes", "").strip(),
        )
        db.session.add(entry)
        db.session.commit()
        flash("Recruiting entry added.", "success")
    return redirect(url_for("athletics.index"))


@athletics_bp.route("/recruiting/<int:entry_id>/edit", methods=["POST"])
@login_required
def edit_recruiting_entry(entry_id):
    entry = RecruitingEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    entry.school_name = request.form.get("school_name", "").strip() or entry.school_name
    entry.division = request.form.get("division", entry.division)
    entry.coach_name = request.form.get("coach_name", "").strip()
    entry.coach_email = request.form.get("coach_email", "").strip()
    entry.coach_phone = request.form.get("coach_phone", "").strip()
    entry.status = request.form.get("status", entry.status)
    entry.scholarship_details = request.form.get("scholarship_details", "").strip()
    entry.notes = request.form.get("notes", "").strip()
    db.session.commit()
    flash("Recruiting entry updated.", "success")
    return redirect(url_for("athletics.index"))


@athletics_bp.route("/recruiting/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete_recruiting_entry(entry_id):
    entry = RecruitingEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash("Recruiting entry deleted.", "info")
    return redirect(url_for("athletics.index"))
