from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import CourseCategory, Course, Level, LevelSubject, Resource, Purchase
from extensions import db

courses_bp = Blueprint("courses", __name__, url_prefix="/courses")

# -------------------------
# Categories page (JHS, SHS, Tertiary)
# -------------------------
@courses_bp.route("/", strict_slashes=False)
def show_categories():
    categories = CourseCategory.query.all()
    return render_template("courses/categories.html", categories=categories)

# -------------------------
# Courses in a category
# -------------------------
@courses_bp.route("/category/<int:category_id>/", strict_slashes=False)
def show_courses(category_id):
    category = CourseCategory.query.get_or_404(category_id)
    return render_template("courses/courses.html", category=category)

# -------------------------
# Levels in a course
# -------------------------
@courses_bp.route("/course/<int:course_id>/levels/", strict_slashes=False)
def show_levels(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template("courses/levels.html", course=course)

# -------------------------
# Subjects in a level
# -------------------------
@courses_bp.route("/level/<int:level_id>/subjects/", strict_slashes=False)
def show_subjects(level_id):
    level = Level.query.get_or_404(level_id)
    core_subjects = [ls.subject for ls in level.level_subjects if ls.subject.subject_type == "core"]
    elective_subjects = [ls.subject for ls in level.level_subjects if ls.subject.subject_type == "elective"]

    return render_template(
        "courses/subjects.html",
        level=level,
        core_subjects=core_subjects,
        elective_subjects=elective_subjects
    )

# -------------------------
# Resources for a subject
# -------------------------

@courses_bp.route("/level/<int:level_id>/subject/<int:subject_id>/resources/", strict_slashes=False)
def show_resources(level_id, subject_id):
    level_subject = LevelSubject.query.filter_by(level_id=level_id, subject_id=subject_id).first_or_404()
    resources = []

    for idx, res in enumerate(level_subject.resources):
        # 🔹 Make the first 3 resources free automatically
        if idx < 3:
            res.is_free = True
            res.price = 0.0

        purchased = False
        if not res.is_free and current_user.is_authenticated:
            purchased = Purchase.query.filter_by(user_id=current_user.id, resource_id=res.id).first() is not None

        resources.append({
            "id": res.id,
            "title": res.title,
            "resource_type": res.resource_type,
            "file_url": res.file_url,
            "author": res.author,
            "can_access": res.is_free or purchased,
            "is_free": res.is_free,
            "price": res.price,
        })

    return render_template(
        "courses/resources.html",
        level_subject=level_subject,
        resources=resources
    )
# ----------------------
# Purchase a paid resource
# -------------------------
@courses_bp.route("/resource/<int:resource_id>/purchase/", strict_slashes=False)
@login_required
def purchase_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)

    # Already purchased
    existing_purchase = Purchase.query.filter_by(user_id=current_user.id, resource_id=resource.id).first()
    if existing_purchase:
        flash("You already have access to this resource.")
        return redirect(url_for(
            "courses.show_resources",
            level_id=resource.level_subject.level_id,
            subject_id=resource.level_subject.subject_id
        ))

    # Free resources don’t need purchase
    if resource.is_free:
        flash("This resource is free. You can access it directly.")
        return redirect(url_for(
            "courses.show_resources",
            level_id=resource.level_subject.level_id,
            subject_id=resource.level_subject.subject_id
        ))

    # Simulate payment
    purchase = Purchase(user_id=current_user.id, resource_id=resource.id, amount_paid=resource.price or 0.0)
    db.session.add(purchase)
    db.session.commit()

    flash(f"You have purchased {resource.title}.")
    return redirect(url_for(
        "courses.show_resources",
        level_id=resource.level_subject.level_id,
        subject_id=resource.level_subject.subject_id
    ))
