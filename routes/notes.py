from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required

from app import db
from models import Task

notes_bp = Blueprint("notes", __name__, url_prefix="/notes")


@notes_bp.route("/", methods=["GET", "POST"])
@login_required
def board():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Title is required.", "danger")
        else:
            task = Task(
                title=title,
                description=request.form.get("description", "").strip(),
                status="To-Do",
            )
            db.session.add(task)
            db.session.commit()
            flash("Task added.", "success")
        return redirect(url_for("notes.board"))

    columns = {status: [] for status in Task.STATUSES}
    for task in Task.query.order_by(Task.updated_at.desc()).all():
        columns.setdefault(task.status, []).append(task)

    return render_template("notes.html", columns=columns, statuses=Task.STATUSES)


@notes_bp.route("/<int:task_id>/move", methods=["POST"])
@login_required
def move_task(task_id):
    task = Task.query.get_or_404(task_id)
    new_status = request.form.get("status")
    if new_status in Task.STATUSES:
        task.status = new_status
        db.session.commit()
    return redirect(url_for("notes.board"))


@notes_bp.route("/<int:task_id>/edit", methods=["POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.title = request.form.get("title", "").strip() or task.title
    task.description = request.form.get("description", "").strip()
    db.session.commit()
    flash("Task updated.", "success")
    return redirect(url_for("notes.board"))


@notes_bp.route("/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted.", "info")
    return redirect(url_for("notes.board"))
