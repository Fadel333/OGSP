from flask import Blueprint, render_template
from models import CourseCategory

home_bp = Blueprint("home", __name__)

@home_bp.route("/", strict_slashes=False)
def index():
    """
    OGSP Public Home Page
    Education.com–style landing page
    """

    # Show limited categories as preview only
    categories = CourseCategory.query.limit(6).all()

    return render_template(
        "home.html",
        categories=categories
    )
