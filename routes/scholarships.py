from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required

from app import db
from models import Scholarship

scholarships_bp = Blueprint("scholarships", __name__, url_prefix="/scholarships")


@scholarships_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Name is required.", "danger")
        else:
            scholarship = Scholarship(
                name=name,
                amount=request.form.get("amount", "").strip(),
                deadline=request.form.get("deadline", "").strip(),
                status=request.form.get("status", "Not Started"),
                notes=request.form.get("notes", "").strip(),
            )
            db.session.add(scholarship)
            db.session.commit()
            flash("Scholarship added.", "success")
        return redirect(url_for("scholarships.index"))

    all_scholarships = Scholarship.query.order_by(Scholarship.updated_at.desc()).all()
    return render_template(
        "scholarships.html",
        scholarships=all_scholarships,
        statuses=Scholarship.STATUSES,
    )


@scholarships_bp.route("/<int:scholarship_id>/edit", methods=["POST"])
@login_required
def edit_scholarship(scholarship_id):
    scholarship = Scholarship.query.get_or_404(scholarship_id)
    scholarship.name = request.form.get("name", "").strip() or scholarship.name
    scholarship.amount = request.form.get("amount", "").strip()
    scholarship.deadline = request.form.get("deadline", "").strip()
    scholarship.status = request.form.get("status", scholarship.status)
    scholarship.notes = request.form.get("notes", "").strip()
    db.session.commit()
    flash("Scholarship updated.", "success")
    return redirect(url_for("scholarships.index"))


@scholarships_bp.route("/<int:scholarship_id>/delete", methods=["POST"])
@login_required
def delete_scholarship(scholarship_id):
    scholarship = Scholarship.query.get_or_404(scholarship_id)
    db.session.delete(scholarship)
    db.session.commit()
    flash("Scholarship deleted.", "info")
    return redirect(url_for("scholarships.index"))
