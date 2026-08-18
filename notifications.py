"""Generates in-app (and, if configured, email) notifications for the current user.

Called opportunistically on each authenticated request (see app.py before_request
hook) so notifications appear without needing a background scheduler/cron job.
Every notification is deduped via Notification.dedupe_key so re-running this on
every page load never creates duplicates.
"""
from datetime import date, timedelta

from app import db
from mailer import send_email
from models import Deadline, Recommender, Notification


def _create_if_new(user, message, link, category, dedupe_key):
    exists = Notification.query.filter_by(user_id=user.id, dedupe_key=dedupe_key).first()
    if exists:
        return None

    notification = Notification(
        user_id=user.id,
        message=message,
        link=link,
        category=category,
        dedupe_key=dedupe_key,
    )
    db.session.add(notification)

    if user.email_notifications_enabled and user.email:
        send_email(user.email, "CollegeOneStop Notification", message)

    return notification


def sync_notifications_for_user(user):
    """Checks for upcoming deadlines and recommender status changes, creating any
    new notifications. Safe to call on every request — cheap queries, dedup-guarded."""
    today = date.today()
    soon = today + timedelta(days=3)

    upcoming_deadlines = Deadline.query.filter(
        Deadline.user_id == user.id,
        Deadline.date >= today,
        Deadline.date <= soon,
    ).all()
    for deadline in upcoming_deadlines:
        days_left = (deadline.date - today).days
        when = "today" if days_left == 0 else f"in {days_left} day{'s' if days_left != 1 else ''}"
        _create_if_new(
            user,
            message=f"Deadline \"{deadline.title}\" is due {when} ({deadline.date.isoformat()}).",
            link="/calendar/",
            category="Deadline",
            dedupe_key=f"deadline:{deadline.id}:{deadline.date.isoformat()}",
        )

    received_recommenders = Recommender.query.filter_by(user_id=user.id, status="Received").all()
    for rec in received_recommenders:
        _create_if_new(
            user,
            message=f"{rec.name} submitted their recommendation letter.",
            link="/applications/recommenders",
            category="Recommender",
            dedupe_key=f"recommender:{rec.id}:Received",
        )

    db.session.commit()
