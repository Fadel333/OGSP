from flask import Blueprint, render_template, abort, jsonify
from flask_login import login_required, current_user
from models import BlogPost, Category

home_bp = Blueprint("home_bp", __name__, url_prefix="/")

# -------------------- Home Page --------------------
@home_bp.route("/")
def index():
    # Get the 3 latest published blog posts
    latest_posts = (
        BlogPost.query
        .filter_by(published=True)
        .order_by(BlogPost.created_at.desc())
        .limit(3)
        .all()
    )

    # Get all categories for the categories preview
    categories = Category.query.all()

    return render_template(
        "home.html",
        categories=categories,
        latest_posts=latest_posts
    )

# -------------------- Individual Blog Post --------------------
@home_bp.route("/post/<slug>")
def view_post(slug):
    post = BlogPost.query.filter_by(slug=slug, published=True).first()
    if not post:
        abort(404)
    return render_template("blog_post.html", post=post)

# -------------------- Debug Route for Admin Status --------------------
@home_bp.route("/debug-admin")
@login_required
def debug_admin():
    """Quick debug route to check current_user.is_admin"""
    return jsonify({
        "email": current_user.email,
        "is_admin": current_user.is_admin
    })
