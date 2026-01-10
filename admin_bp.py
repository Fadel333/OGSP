from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models import BlogPost
from extensions import db
from slugify import slugify
from werkzeug.utils import secure_filename
import os
import time
from functools import wraps

admin_bp = Blueprint("admin_bp", __name__,)

# -------------------- Admin-only decorator --------------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(current_user, "is_admin", False):
            flash("Access denied.", "danger")
            return redirect(url_for("home_bp.index"))  # adjust if your home blueprint is named differently
        return f(*args, **kwargs)
    return decorated_function

# -------------------- File Upload Helpers --------------------
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mov", "avi"}

def allowed_file(filename, type="image"):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    if type == "image":
        return ext in ALLOWED_IMAGE_EXTENSIONS
    return ext in ALLOWED_VIDEO_EXTENSIONS

def save_file(file, folder="uploads"):
    """Save file to static/uploads and return filename"""
    if not file:
        return None
    filename = f"{int(time.time())}_{secure_filename(file.filename)}"
    save_path = os.path.join(current_app.root_path, "static", folder, filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    file.save(save_path)
    return filename

# -------------------- Dashboard --------------------
@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template("admin/dashboard.html", posts=posts)

# -------------------- Add New Blog Post --------------------
@admin_bp.route("/post/new", methods=["GET", "POST"])
@login_required
@admin_required
def add_post():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        published = bool(request.form.get("published"))
        image_file = request.files.get("image")
        video_file = request.files.get("video")

        if not title or not content:
            flash("Title and content are required.", "danger")
            return redirect(url_for("admin_bp.add_post"))

        # Save files
        image_filename = save_file(image_file, "uploads/images") if image_file and allowed_file(image_file.filename, "image") else None
        video_filename = save_file(video_file, "uploads/videos") if video_file and allowed_file(video_file.filename, "video") else None

        slug = slugify(title)
        new_post = BlogPost(
            title=title,
            slug=slug,
            content=content,
            published=published,
            image=image_filename,
            video=video_filename
        )
        db.session.add(new_post)
        db.session.commit()
        flash("Blog post created successfully!", "success")
        return redirect(url_for("admin_bp.dashboard"))

    return render_template("admin/add_post.html")

# -------------------- Edit Blog Post --------------------
@admin_bp.route("/post/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)

    if request.method == "POST":
        post.title = request.form.get("title")
        post.content = request.form.get("content")
        post.published = bool(request.form.get("published"))
        image_file = request.files.get("image")
        video_file = request.files.get("video")

        if not post.title or not post.content:
            flash("Title and content are required.", "danger")
            return redirect(url_for("admin_bp.edit_post", post_id=post_id))

        # Update files if provided
        if image_file and allowed_file(image_file.filename, "image"):
            post.image = save_file(image_file, "uploads/images")
        if video_file and allowed_file(video_file.filename, "video"):
            post.video = save_file(video_file, "uploads/videos")

        post.slug = slugify(post.title)
        db.session.commit()
        flash("Blog post updated successfully!", "success")
        return redirect(url_for("admin_bp.dashboard"))

    return render_template("admin/edit_post.html", post=post)

# -------------------- Delete Blog Post --------------------
@admin_bp.route("/post/delete/<int:post_id>", methods=["POST"])
@login_required
@admin_required
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Blog post deleted successfully!", "success")
    return redirect(url_for("admin_bp.dashboard"))
