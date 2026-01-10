from flask import render_template
from flask_login import login_required
from . import user_bp
from flask_login import current_user
from models import Notification
from extensions import db



@user_bp.route("/library")
@login_required
def library():
    return render_template("library.html")



@user_bp.route("/notifications")
@login_required
def notifications():
    notifications = Notification.query \
        .filter_by(user_id=current_user.id) \
        .order_by(Notification.created_at.desc()) \
        .all()

    return render_template(
        "notifications.html",
        notifications=notifications
    )

@user_bp.route("/notifications/read")
@login_required
def mark_notifications_read():
    Notification.query \
        .filter_by(user_id=current_user.id, is_read=False) \
        .update({"is_read": True})

    db.session.commit()
    return "", 204


@user_bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html")
