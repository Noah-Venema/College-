from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required

from app import db
from models import FinancialAid, Scholarship
from routes.scholarships import _parse_amount

financial_aid_bp = Blueprint("financial_aid", __name__, url_prefix="/financial-aid")


def _tracked_aid_totals():
    """Sum received/awarded aid from existing trackers, grouped for calculator pre-fill."""
    received = FinancialAid.query.filter_by(status="Received").all()
    grants = sum(_parse_amount(a.amount) for a in received if a.source in ("Grant", "FAFSA"))
    loans = sum(_parse_amount(a.amount) for a in received if a.source == "Loan")
    work_study = sum(_parse_amount(a.amount) for a in received if a.source == "Work-Study")
    other = sum(_parse_amount(a.amount) for a in received if a.source == "Other")
    scholarships = sum(
        _parse_amount(s.amount) for s in Scholarship.query.filter_by(status="Awarded").all()
    )
    return {
        "grants_scholarships": round(grants + scholarships, 2),
        "loans": round(loans, 2),
        "work_study": round(work_study, 2),
        "other": round(other, 2),
    }


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
        tracked_aid_totals=_tracked_aid_totals(),
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
