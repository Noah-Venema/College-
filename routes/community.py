from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import or_, and_

from app import db
from models import User, Friendship, Post, Comment

community_bp = Blueprint("community", __name__, url_prefix="/community")


def _friendship_between(user_a_id, user_b_id):
    return Friendship.query.filter(
        or_(
            and_(Friendship.requester_id == user_a_id, Friendship.addressee_id == user_b_id),
            and_(Friendship.requester_id == user_b_id, Friendship.addressee_id == user_a_id),
        )
    ).first()


def _are_friends(user_a_id, user_b_id):
    friendship = _friendship_between(user_a_id, user_b_id)
    return bool(friendship and friendship.status == "accepted")


def _friend_ids(user_id):
    accepted = Friendship.query.filter(
        Friendship.status == "accepted",
        or_(Friendship.requester_id == user_id, Friendship.addressee_id == user_id),
    ).all()
    ids = set()
    for f in accepted:
        ids.add(f.addressee_id if f.requester_id == user_id else f.requester_id)
    return ids


def _visible_post_ids_query():
    """Posts visible to current_user: their own, any public post, or friends-only posts from a friend."""
    friend_ids = _friend_ids(current_user.id)
    return Post.query.filter(
        or_(
            Post.author_id == current_user.id,
            Post.visibility == "public",
            and_(Post.visibility == "friends", Post.author_id.in_(friend_ids)) if friend_ids else False,
        )
    )


@community_bp.route("/")
@login_required
def feed():
    filter_type = request.args.get("filter", "all")
    query = _visible_post_ids_query()
    if filter_type == "public":
        query = query.filter(Post.visibility == "public")
    elif filter_type == "friends":
        friend_ids = _friend_ids(current_user.id)
        query = query.filter(Post.visibility == "friends", Post.author_id.in_(friend_ids or [-1]))

    posts = query.order_by(Post.created_at.desc()).all()
    return render_template("community/feed.html", posts=posts, filter_type=filter_type)


@community_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        visibility = request.form.get("visibility", "public")
        if visibility not in Post.VISIBILITIES:
            visibility = "public"
        if not title:
            flash("Title is required.", "danger")
        else:
            post = Post(author_id=current_user.id, title=title, body=body, visibility=visibility)
            db.session.add(post)
            db.session.commit()
            flash("Post created!", "success")
            return redirect(url_for("community.feed"))
    return render_template("community/new_post.html")


@community_bp.route("/post/<int:post_id>")
@login_required
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        if post.visibility == "friends" and not _are_friends(current_user.id, post.author_id):
            abort(403)
    return render_template("community/post_detail.html", post=post)


@community_bp.route("/post/<int:post_id>/comment", methods=["POST"])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        if post.visibility == "friends" and not _are_friends(current_user.id, post.author_id):
            abort(403)
    body = request.form.get("body", "").strip()
    if not body:
        flash("Comment can't be empty.", "danger")
    else:
        comment = Comment(post_id=post.id, author_id=current_user.id, body=body)
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for("community.view_post", post_id=post.id))


@community_bp.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.filter_by(id=post_id, author_id=current_user.id).first_or_404()
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.", "info")
    return redirect(url_for("community.feed"))


@community_bp.route("/friends", methods=["GET"])
@login_required
def friends():
    accepted = Friendship.query.filter(
        Friendship.status == "accepted",
        or_(Friendship.requester_id == current_user.id, Friendship.addressee_id == current_user.id),
    ).all()
    friend_entries = []
    friend_ids = set()
    for f in accepted:
        other_id = f.addressee_id if f.requester_id == current_user.id else f.requester_id
        friend_ids.add(other_id)
        friend_entries.append({"user": User.query.get(other_id), "friendship_id": f.id})
    friend_entries.sort(key=lambda e: e["user"].username.lower())

    incoming = Friendship.query.filter_by(addressee_id=current_user.id, status="pending").all()
    outgoing = Friendship.query.filter_by(requester_id=current_user.id, status="pending").all()

    search_query = request.args.get("q", "").strip()
    search_results = []
    if search_query:
        existing_pair_ids = friend_ids | {current_user.id}
        pending_ids = {f.addressee_id for f in outgoing} | {f.requester_id for f in incoming}
        search_results = (
            User.query.filter(User.username.ilike(f"%{search_query}%"))
            .filter(~User.id.in_(existing_pair_ids | pending_ids))
            .order_by(User.username.asc())
            .limit(20)
            .all()
        )

    return render_template(
        "community/friends.html",
        friend_entries=friend_entries,
        incoming=incoming,
        outgoing=outgoing,
        search_query=search_query,
        search_results=search_results,
    )


@community_bp.route("/friends/request/<int:user_id>", methods=["POST"])
@login_required
def send_request(user_id):
    if user_id == current_user.id:
        flash("You can't friend yourself.", "danger")
        return redirect(url_for("community.friends"))

    target = User.query.get_or_404(user_id)
    existing = _friendship_between(current_user.id, target.id)
    if existing:
        flash(f"A friend request with {target.username} already exists.", "info")
    else:
        friendship = Friendship(requester_id=current_user.id, addressee_id=target.id, status="pending")
        db.session.add(friendship)
        db.session.commit()
        flash(f"Friend request sent to {target.username}.", "success")
    return redirect(url_for("community.friends"))


@community_bp.route("/friends/<int:friendship_id>/accept", methods=["POST"])
@login_required
def accept_request(friendship_id):
    friendship = Friendship.query.filter_by(id=friendship_id, addressee_id=current_user.id).first_or_404()
    friendship.status = "accepted"
    db.session.commit()
    flash(f"You are now friends with {friendship.requester.username}.", "success")
    return redirect(url_for("community.friends"))


@community_bp.route("/friends/<int:friendship_id>/decline", methods=["POST"])
@login_required
def decline_request(friendship_id):
    friendship = Friendship.query.filter_by(id=friendship_id, addressee_id=current_user.id).first_or_404()
    db.session.delete(friendship)
    db.session.commit()
    flash("Friend request declined.", "info")
    return redirect(url_for("community.friends"))


@community_bp.route("/friends/<int:friendship_id>/remove", methods=["POST"])
@login_required
def remove_friend(friendship_id):
    friendship = Friendship.query.filter(
        Friendship.id == friendship_id,
        or_(Friendship.requester_id == current_user.id, Friendship.addressee_id == current_user.id),
    ).first_or_404()
    db.session.delete(friendship)
    db.session.commit()
    flash("Friend removed.", "info")
    return redirect(url_for("community.friends"))
