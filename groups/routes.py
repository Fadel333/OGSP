from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Group, GroupMember, DiscussionMessage, Notification, GroupJoinRequest, User
from datetime import datetime, timedelta

groups_bp = Blueprint("groups", __name__)

# ------------------------- LIST GROUPS -------------------------
@groups_bp.route("/", methods=["GET"])
@login_required
def list_groups():
    search_query = request.args.get("q", "")
    groups = Group.query.filter(Group.name.ilike(f"%{search_query}%")).all() if search_query else Group.query.all()
    return render_template("groups/list.html", groups=groups, search_query=search_query)


# ------------------------- CREATE GROUP -------------------------
@groups_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_group():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name:
            flash("Group name is required", "error")
            return redirect(url_for("groups.create_group"))

        group = Group(name=name, description=description, owner_id=current_user.id)
        db.session.add(group)
        db.session.commit()

        # Auto-join creator
        member = GroupMember(user_id=current_user.id, group_id=group.id, is_approved=True, joined_at=datetime.utcnow())
        db.session.add(member)
        db.session.commit()

        flash("Group created successfully 🎉", "success")
        return redirect(url_for("groups.group_detail", group_id=group.id))

    return render_template("groups/create.html")


# ------------------------- GROUP DETAIL + DISCUSSION -------------------------
@groups_bp.route("/<int:group_id>", methods=["GET", "POST"])
@login_required
def group_detail(group_id):
    group = Group.query.get_or_404(group_id)
    membership = GroupMember.query.filter_by(user_id=current_user.id, group_id=group.id).first()
    is_member = membership.is_approved if membership else False

    if request.method == "POST":
        if not is_member:
            flash("You must be a member to send messages.", "error")
            return redirect(url_for("groups.group_detail", group_id=group.id))

        message_text = request.form.get("message")
        if not message_text:
            flash("Message cannot be empty.", "error")
            return redirect(url_for("groups.group_detail", group_id=group.id))

        msg = DiscussionMessage(group_id=group.id, user_id=current_user.id, message=message_text)
        db.session.add(msg)

        # Notify other members
        members = GroupMember.query.filter_by(group_id=group.id, is_approved=True).all()
        for member in members:
            if member.user_id != current_user.id:
                notification = Notification(
                    user_id=member.user_id,
                    message=f"New message in {group.name} from {current_user.name}",
                    link=url_for("groups.group_detail", group_id=group.id)
                )
                db.session.add(notification)

        db.session.commit()
        return redirect(url_for("groups.group_detail", group_id=group.id))

    # GET MESSAGES
    messages = DiscussionMessage.query.filter_by(group_id=group.id).order_by(DiscussionMessage.timestamp.asc()).all() if is_member else []

    pending_request = GroupJoinRequest.query.filter_by(user_id=current_user.id, group_id=group.id, status="pending").first()
    join_requests = GroupJoinRequest.query.filter_by(group_id=group.id, status="pending").all() if group.owner_id == current_user.id else []

    return render_template(
        "groups/detail.html",
        group=group,
        messages=messages,
        is_member=is_member,
        pending_request=pending_request,
        join_requests=join_requests
    )


# ------------------------- REQUEST TO JOIN GROUP -------------------------
@groups_bp.route("/<int:group_id>/request", methods=["POST"])
@login_required
def request_join(group_id):
    group = Group.query.get_or_404(group_id)
    if GroupMember.query.filter_by(user_id=current_user.id, group_id=group.id).first():
        flash("You are already a member.", "info")
        return redirect(url_for("groups.group_detail", group_id=group.id))

    if GroupJoinRequest.query.filter_by(user_id=current_user.id, group_id=group.id, status="pending").first():
        flash("Join request already sent.", "info")
        return redirect(url_for("groups.group_detail", group_id=group.id))

    join_request = GroupJoinRequest(user_id=current_user.id, group_id=group.id)
    db.session.add(join_request)

    notification = Notification(
        user_id=group.owner_id,
        message=f"{current_user.name} requested to join {group.name}",
        link=url_for("groups.group_detail", group_id=group.id)
    )
    db.session.add(notification)
    db.session.commit()

    flash("Join request sent. Awaiting approval.", "success")
    return redirect(url_for("groups.group_detail", group_id=group.id))


# ------------------------- APPROVE / REJECT REQUEST -------------------------
@groups_bp.route("/requests/<int:request_id>/approve", methods=["POST"])
@login_required
def approve_request(request_id):
    req = GroupJoinRequest.query.get_or_404(request_id)
    group = req.group
    if group.owner_id != current_user.id:
        flash("You are not authorized.", "error")
        return redirect(url_for("groups.list_groups"))

    member = GroupMember(user_id=req.user_id, group_id=group.id, is_approved=True, joined_at=datetime.utcnow())
    db.session.add(member)
    req.status = "approved"

    notification = Notification(
        user_id=req.user_id,
        message=f"Your request to join {group.name} was approved",
        link=url_for("groups.group_detail", group_id=group.id)
    )
    db.session.add(notification)
    db.session.commit()

    flash("Request approved.", "success")
    return redirect(url_for("groups.group_detail", group_id=group.id))


@groups_bp.route("/requests/<int:request_id>/reject", methods=["POST"])
@login_required
def reject_request(request_id):
    req = GroupJoinRequest.query.get_or_404(request_id)
    group = req.group
    if group.owner_id != current_user.id:
        flash("You are not authorized.", "error")
        return redirect(url_for("groups.list_groups"))

    req.status = "rejected"
    notification = Notification(
        user_id=req.user_id,
        message=f"Your request to join {group.name} was rejected",
        link=url_for("groups.group_detail", group_id=group.id)
    )
    db.session.add(notification)
    db.session.commit()

    flash("Request rejected.", "info")
    return redirect(url_for("groups.group_detail", group_id=group.id))


# ------------------------- LEAVE GROUP -------------------------
@groups_bp.route("/<int:group_id>/leave", methods=["POST"])
@login_required
def leave_group(group_id):
    membership = GroupMember.query.filter_by(user_id=current_user.id, group_id=group_id).first()
    if not membership:
        flash("You are not a member of this group.", "error")
        return redirect(url_for("groups.list_groups"))

    db.session.delete(membership)
    db.session.commit()
    flash("You left the group.", "success")
    return redirect(url_for("groups.list_groups"))


# ------------------------- GROUP MESSAGES (Online Members) -------------------------
@groups_bp.route("/<int:group_id>/messages")
@login_required
def group_messages(group_id):
    membership = GroupMember.query.filter_by(user_id=current_user.id, group_id=group_id).first()
    if not membership:
        return "", 403

    messages = DiscussionMessage.query.filter_by(group_id=group_id).order_by(DiscussionMessage.timestamp.asc()).all()

    # Update last_active for online tracking
    current_user.last_active = datetime.utcnow()
    db.session.commit()

    two_minutes_ago = datetime.utcnow() - timedelta(minutes=2)
    online_members = GroupMember.query.join(User).filter(
        GroupMember.group_id == group_id,
        User.last_active >= two_minutes_ago
    ).all()

    return render_template("groups/_messages.html", messages=messages, online_count=len(online_members))
