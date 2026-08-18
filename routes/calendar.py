import json
from datetime import datetime, date, timedelta

from flask import Blueprint, render_template, redirect, url_for, request, flash, Response, abort
from flask_login import login_required, current_user

from app import db
from models import Deadline, User

calendar_bp = Blueprint("calendar", __name__, url_prefix="/calendar")


@calendar_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        date_str = request.form.get("date", "").strip()

        if not title or not date_str:
            flash("Title and date are required.", "danger")
        else:
            try:
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date format.", "danger")
                return redirect(url_for("calendar.index"))

            deadline = Deadline(
                user_id=current_user.id,
                title=title,
                date=parsed_date,
                category=request.form.get("category", "Other"),
                notes=request.form.get("notes", "").strip(),
            )
            db.session.add(deadline)
            db.session.commit()
            flash("Deadline added.", "success")
        return redirect(url_for("calendar.index"))

    all_deadlines = Deadline.query.filter_by(user_id=current_user.id).order_by(Deadline.date.asc()).all()
    feed_url = url_for(
        "calendar.feed", token=current_user.calendar_token, _external=True
    )
    mini_calendar_events = [
        {
            "date": d.date.isoformat(),
            "title": d.title,
            "category": d.category,
            "notes": d.notes or "",
        }
        for d in all_deadlines
    ]
    return render_template(
        "calendar.html",
        deadlines=all_deadlines,
        categories=Deadline.CATEGORIES,
        feed_url=feed_url,
        today=date.today(),
        mini_calendar_events_json=json.dumps(mini_calendar_events),
    )


@calendar_bp.route("/<int:deadline_id>/edit", methods=["POST"])
@login_required
def edit_deadline(deadline_id):
    deadline = Deadline.query.filter_by(id=deadline_id, user_id=current_user.id).first_or_404()
    deadline.title = request.form.get("title", "").strip() or deadline.title
    date_str = request.form.get("date", "").strip()
    if date_str:
        try:
            deadline.date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format.", "danger")
            return redirect(url_for("calendar.index"))
    deadline.category = request.form.get("category", deadline.category)
    deadline.notes = request.form.get("notes", "").strip()
    db.session.commit()
    flash("Deadline updated.", "success")
    return redirect(url_for("calendar.index"))


@calendar_bp.route("/<int:deadline_id>/delete", methods=["POST"])
@login_required
def delete_deadline(deadline_id):
    deadline = Deadline.query.filter_by(id=deadline_id, user_id=current_user.id).first_or_404()
    db.session.delete(deadline)
    db.session.commit()
    flash("Deadline deleted.", "info")
    return redirect(url_for("calendar.index"))


def _ics_escape(text):
    return (text or "").replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


@calendar_bp.route("/feed/<token>.ics")
def feed(token):
    """Public .ics feed (no login) so Google/Apple Calendar can subscribe directly.

    Authenticated by an unguessable per-user token instead of a session,
    since external calendar apps can't send login cookies.
    """
    user = User.query.filter_by(calendar_token=token).first()
    if user is None:
        abort(404)

    deadlines = Deadline.query.filter_by(user_id=user.id).order_by(Deadline.date.asc()).all()

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//CollegeOneStop//Deadlines//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:CollegeOneStop Deadlines",
    ]

    for d in deadlines:
        start = d.date.strftime("%Y%m%d")
        end = (d.date + timedelta(days=1)).strftime("%Y%m%d")
        summary = _ics_escape(f"[{d.category}] {d.title}")
        description = _ics_escape(d.notes or "")
        lines += [
            "BEGIN:VEVENT",
            f"UID:deadline-{d.id}@collegeonestop",
            f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART;VALUE=DATE:{start}",
            f"DTEND;VALUE=DATE:{end}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
            "END:VEVENT",
        ]

    lines.append("END:VCALENDAR")
    ics_content = "\r\n".join(lines) + "\r\n"

    return Response(
        ics_content,
        mimetype="text/calendar",
        headers={"Content-Disposition": "inline; filename=collegeonestop-deadlines.ics"},
    )
