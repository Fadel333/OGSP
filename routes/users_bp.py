from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from utils import send_email
import uuid

users_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/user"
)

# =============================
# PROFILE PAGE & UPDATE
# =============================
@users_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()

        if not name or not email:
            flash("Name and email are required.", "danger")
            return redirect(url_for("users.profile"))

        # prevent duplicate email
        existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing_user:
            flash("This email is already in use.", "danger")
            return redirect(url_for("users.profile"))

        current_user.name = name
        current_user.email = email
        db.session.commit()

        flash("Profile updated successfully.", "success")
        return redirect(url_for("users.profile"))

    return render_template("profile.html")


# =============================
# CHANGE PASSWORD
# =============================
@users_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not current_user.check_password(current_password):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("users.change_password"))

        if new_password != confirm_password:
            flash("New passwords do not match.", "danger")
            return redirect(url_for("users.change_password"))

        current_user.set_password(new_password)
        db.session.commit()
        flash("Password updated successfully.", "success")
        return redirect(url_for("users.profile"))

    return render_template("change_password.html")


# =============================
# FORGOT PASSWORD - REQUEST RESET
# =============================
@users_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.generate_reset_token()
            reset_url = url_for("users.reset_password", token=token, _external=True)
            send_email(
                user.email,
                "Password Reset Request",
                f"Hello {user.name},\n\nClick the link below to reset your password:\n{reset_url}\n\nThis link expires in 1 hour."
            )
            flash(f"Password reset link sent to {email}.", "success")
        else:
            flash("No user found with that email.", "danger")
        return redirect(url_for("users.forgot_password"))

    return render_template("forgot_password.html")


# =============================
# RESET PASSWORD
# =============================
@users_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.query.filter_by(reset_password_token=token).first()
    if not user:
        flash("Invalid or expired reset token.", "danger")
        return redirect(url_for("users.forgot_password"))

    # Check expiry
    if user.reset_token_expiry < datetime.utcnow():
        flash("Reset token expired.", "danger")
        return redirect(url_for("users.forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("users.reset_password", token=token))

        user.set_password(new_password)
        user.reset_password_token = None
        user.reset_token_expiry = None
        db.session.commit()

        flash("Password reset successfully. You can now login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token)


# =============================
# EMAIL VERIFICATION
# =============================
@users_bp.route("/verify-email/<token>")
def verify_email(token):
    user = User.query.filter_by(email_verification_token=token).first()
    if not user:
        flash("Invalid verification token.", "danger")
        return redirect(url_for("auth.login"))

    user.email_verified = True
    user.email_verification_token = None
    db.session.commit()
    flash("Email verified successfully.", "success")
    return redirect(url_for("auth.login"))
