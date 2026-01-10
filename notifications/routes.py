from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from models import Notification, db

notifications_bp = Blueprint("notifications", __name__, url_prefix="/user/notifications")

# -------------------------
# Show all notifications
# -------------------------
@notifications_bp.route("/", strict_slashes=False)
@login_required
def list_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id)\
                                     .order_by(Notification.created_at.desc()).all()
    return render_template("notification.html", notifications=notifications)

# -------------------------
# Mark a notification as read
# -------------------------
@notifications_bp.route("/read/<int:notification_id>/", strict_slashes=False)
@login_required
def mark_as_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        flash("You cannot modify this notification.")
        return redirect(url_for("notifications.list_notifications"))

    notification.is_read = True
    db.session.commit()
    flash("Notification marked as read.")
    return redirect(url_for("notifications.list_notifications"))
