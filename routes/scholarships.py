import re

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required

from app import db
from models import Scholarship

scholarships_bp = Blueprint("scholarships", __name__, url_prefix="/scholarships")


def _parse_amount(amount_str):
    """Best-effort parse of a free-text amount field (e.g. "$1,000.50") into a float.

    Returns 0.0 if nothing numeric can be found, since amounts are stored as
    free text and aren't guaranteed to be well-formed.
    """
    if not amount_str:
        return 0.0
    match = re.search(r"[\d,]+(?:\.\d+)?", amount_str)
    if not match:
        return 0.0
    try:
        return float(match.group().replace(",", ""))
    except ValueError:
        return 0.0


def _format_currency(value):
    return f"${value:,.2f}" if value % 1 else f"${value:,.0f}"


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

    total_applied = sum(_parse_amount(s.amount) for s in all_scholarships)
    total_won = sum(_parse_amount(s.amount) for s in all_scholarships if s.status == "Awarded")

    return render_template(
        "scholarships.html",
        scholarships=all_scholarships,
        statuses=Scholarship.STATUSES,
        total_applied=_format_currency(total_applied),
        total_won=_format_currency(total_won),
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


@scholarships_bp.route("/<int:scholarship_id>/mark-awarded", methods=["POST"])
@login_required
def mark_awarded(scholarship_id):
    scholarship = Scholarship.query.get_or_404(scholarship_id)
    scholarship.status = "Awarded"
    db.session.commit()
    flash(f'"{scholarship.name}" marked as Awarded! 🎉', "success")
    return redirect(url_for("scholarships.index"))


@scholarships_bp.route("/<int:scholarship_id>/delete", methods=["POST"])
@login_required
def delete_scholarship(scholarship_id):
    scholarship = Scholarship.query.get_or_404(scholarship_id)
    db.session.delete(scholarship)
    db.session.commit()
    flash("Scholarship deleted.", "info")
    return redirect(url_for("scholarships.index"))
