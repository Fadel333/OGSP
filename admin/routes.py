from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import BlogPost
from extensions import db
from slugify import slugify

# -------------------- Blueprint --------------------
admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

# -------------------- Helper: admin-only access --------------------
def admin_required():
    if not getattr(current_user, "is_admin", False):
        flash("Access denied.", "danger")
        return redirect(url_for("home_bp.index"))  # corrected to your home blueprint
    return True

# -------------------- Default /admin route redirects to dashboard --------------------
@admin_bp.route("/")
@login_required
def index():
    # redirect automatically to the dashboard
    return redirect(url_for("admin_bp.dashboard"))

# -------------------- Dashboard --------------------
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if not getattr(current_user, "is_admin", False):
        flash("Access denied.", "danger")
        return redirect(url_for("home_bp.index"))

    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template("admin/dashboard.html", posts=posts)

# -------------------- Add New Blog Post --------------------
@admin_bp.route("/post/new", methods=["GET", "POST"])
@login_required
def add_post():
    if not getattr(current_user, "is_admin", False):
        flash("Access denied.", "danger")
        return redirect(url_for("home_bp.index"))

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        published = bool(request.form.get("published"))

        if not title or not content:
            flash("Title and content are required.", "danger")
            return redirect(url_for("admin_bp.add_post"))

        slug = slugify(title)
        new_post = BlogPost(title=title, slug=slug, content=content, published=published)
        db.session.add(new_post)
        db.session.commit()
        flash("Blog post created successfully!", "success")
        return redirect(url_for("admin_bp.dashboard"))

    return render_template("admin/add_post.html")

# -------------------- Edit Blog Post --------------------
@admin_bp.route("/post/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    if not getattr(current_user, "is_admin", False):
        flash("Access denied.", "danger")
        return redirect(url_for("home_bp.index"))

    post = BlogPost.query.get_or_404(post_id)

    if request.method == "POST":
        post.title = request.form.get("title")
        post.content = request.form.get("content")
        post.published = bool(request.form.get("published"))

        if not post.title or not post.content:
            flash("Title and content are required.", "danger")
            return redirect(url_for("admin_bp.edit_post", post_id=post_id))

        post.slug = slugify(post.title)
        db.session.commit()
        flash("Blog post updated successfully!", "success")
        return redirect(url_for("admin_bp.dashboard"))

    return render_template("admin/edit_post.html", post=post)

# -------------------- Delete Blog Post --------------------
@admin_bp.route("/post/delete/<int:post_id>", methods=["POST"])
@login_required
def delete_post(post_id):
    if not getattr(current_user, "is_admin", False):
        flash("Access denied.", "danger")
        return redirect(url_for("home_bp.index"))

    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Blog post deleted successfully!", "success")
    return redirect(url_for("admin_bp.dashboard"))
