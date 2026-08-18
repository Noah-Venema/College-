from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from app import db
from models import Notification
from notifications import sync_notifications_for_user

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@notifications_bp.route("/")
@login_required
def index():
    sync_notifications_for_user(current_user)
    all_notifications = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return render_template("notifications/index.html", notifications=all_notifications)


@notifications_bp.route("/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_read(notification_id):
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    notification.is_read = True
    db.session.commit()
    return redirect(request.referrer or url_for("notifications.index"))


@notifications_bp.route("/read-all", methods=["POST"])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    return redirect(request.referrer or url_for("notifications.index"))


@notifications_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        enabled = request.form.get("email_notifications_enabled") == "on"
        current_user.email = email or None
        current_user.email_notifications_enabled = enabled and bool(email)
        db.session.commit()
        flash("Notification settings saved.", "success")
        return redirect(url_for("notifications.settings"))

    return render_template("notifications/settings.html")
