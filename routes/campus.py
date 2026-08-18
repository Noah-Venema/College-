from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from app import db
from models import Campus

campus_bp = Blueprint("campus", __name__, url_prefix="/campus")


@campus_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        school_name = request.form.get("school_name", "").strip()
        if not school_name:
            flash("School name is required.", "danger")
        else:
            campus = Campus(
                user_id=current_user.id,
                school_name=school_name,
                housing_info=request.form.get("housing_info", "").strip(),
                food_info=request.form.get("food_info", "").strip(),
                student_ratio=request.form.get("student_ratio", "").strip(),
                notes=request.form.get("notes", "").strip(),
            )
            db.session.add(campus)
            db.session.commit()
            flash("Campus info added.", "success")
        return redirect(url_for("campus.index"))

    all_campuses = Campus.query.filter_by(user_id=current_user.id).order_by(Campus.school_name.asc()).all()
    return render_template("campus.html", campuses=all_campuses)


@campus_bp.route("/<int:campus_id>/edit", methods=["POST"])
@login_required
def edit_campus(campus_id):
    campus = Campus.query.filter_by(id=campus_id, user_id=current_user.id).first_or_404()
    campus.school_name = request.form.get("school_name", "").strip() or campus.school_name
    campus.housing_info = request.form.get("housing_info", "").strip()
    campus.food_info = request.form.get("food_info", "").strip()
    campus.student_ratio = request.form.get("student_ratio", "").strip()
    campus.notes = request.form.get("notes", "").strip()
    db.session.commit()
    flash("Campus info updated.", "success")
    return redirect(url_for("campus.index"))


@campus_bp.route("/<int:campus_id>/delete", methods=["POST"])
@login_required
def delete_campus(campus_id):
    campus = Campus.query.filter_by(id=campus_id, user_id=current_user.id).first_or_404()
    db.session.delete(campus)
    db.session.commit()
    flash("Campus info deleted.", "info")
    return redirect(url_for("campus.index"))
