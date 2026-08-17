from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required

from app import db
from models import FinancialAid

financial_aid_bp = Blueprint("financial_aid", __name__, url_prefix="/financial-aid")


@financial_aid_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        source = request.form.get("source", "Other")
        amount = request.form.get("amount", "").strip()
        if not source:
            flash("Source is required.", "danger")
        else:
            aid = FinancialAid(
                source=source,
                name=request.form.get("name", "").strip(),
                amount=amount,
                status=request.form.get("status", "Pending"),
                notes=request.form.get("notes", "").strip(),
            )
            db.session.add(aid)
            db.session.commit()
            flash("Financial aid entry added.", "success")
        return redirect(url_for("financial_aid.index"))

    all_aid = FinancialAid.query.order_by(FinancialAid.updated_at.desc()).all()
    return render_template(
        "financial_aid.html",
        aid_entries=all_aid,
        sources=FinancialAid.SOURCES,
        statuses=FinancialAid.STATUSES,
    )


@financial_aid_bp.route("/<int:aid_id>/edit", methods=["POST"])
@login_required
def edit_aid(aid_id):
    aid = FinancialAid.query.get_or_404(aid_id)
    aid.source = request.form.get("source", aid.source)
    aid.name = request.form.get("name", "").strip()
    aid.amount = request.form.get("amount", "").strip()
    aid.status = request.form.get("status", aid.status)
    aid.notes = request.form.get("notes", "").strip()
    db.session.commit()
    flash("Financial aid entry updated.", "success")
    return redirect(url_for("financial_aid.index"))


@financial_aid_bp.route("/<int:aid_id>/delete", methods=["POST"])
@login_required
def delete_aid(aid_id):
    aid = FinancialAid.query.get_or_404(aid_id)
    db.session.delete(aid)
    db.session.commit()
    flash("Financial aid entry deleted.", "info")
    return redirect(url_for("financial_aid.index"))
