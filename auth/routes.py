from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from extensions import db
from models import User, GroupMember

auth_bp = Blueprint("auth", __name__)

# -------------------------
# REGISTER
# -------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not name or not email or not password:
            flash("All fields are required")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(username=username).first():
            flash("Username already taken")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for("auth.register"))

        user = User(
            username=username,
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please login.")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", hide_nav_links=True)


# -------------------------
# LOGIN
# -------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(username=username, email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Login successful")
            return redirect(url_for("auth.dashboard"))

        flash("Invalid username, email, or password")
        return redirect(url_for("auth.login"))

    return render_template("auth/login.html", hide_nav_links=True)


# -------------------------
# DASHBOARD
# -------------------------
@auth_bp.route("/dashboard")
@login_required
def dashboard():
    memberships = GroupMember.query.filter_by(user_id=current_user.id).all()
    groups = [m.group for m in memberships]

    return render_template(
        "auth/dashboard.html",
        user=current_user,
        groups=groups
    )


# -------------------------
# LOGOUT
# -------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out")
    return redirect(url_for("auth.login"))
