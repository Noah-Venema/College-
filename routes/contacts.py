from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from app import db
from models import Contact

contacts_bp = Blueprint("contacts", __name__, url_prefix="/contacts")


@contacts_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Name is required.", "danger")
        else:
            contact = Contact(
                user_id=current_user.id,
                name=name,
                role=request.form.get("role", "Other"),
                organization=request.form.get("organization", "").strip(),
                email=request.form.get("email", "").strip(),
                phone=request.form.get("phone", "").strip(),
                notes=request.form.get("notes", "").strip(),
            )
            db.session.add(contact)
            db.session.commit()
            flash("Contact added.", "success")
        return redirect(url_for("contacts.index"))

    all_contacts = Contact.query.filter_by(user_id=current_user.id).order_by(Contact.name.asc()).all()
    return render_template("contacts.html", contacts=all_contacts, roles=Contact.ROLES)


@contacts_bp.route("/<int:contact_id>/edit", methods=["POST"])
@login_required
def edit_contact(contact_id):
    contact = Contact.query.filter_by(id=contact_id, user_id=current_user.id).first_or_404()
    contact.name = request.form.get("name", "").strip() or contact.name
    contact.role = request.form.get("role", contact.role)
    contact.organization = request.form.get("organization", "").strip()
    contact.email = request.form.get("email", "").strip()
    contact.phone = request.form.get("phone", "").strip()
    contact.notes = request.form.get("notes", "").strip()
    db.session.commit()
    flash("Contact updated.", "success")
    return redirect(url_for("contacts.index"))


@contacts_bp.route("/<int:contact_id>/delete", methods=["POST"])
@login_required
def delete_contact(contact_id):
    contact = Contact.query.filter_by(id=contact_id, user_id=current_user.id).first_or_404()
    db.session.delete(contact)
    db.session.commit()
    flash("Contact deleted.", "info")
    return redirect(url_for("contacts.index"))
