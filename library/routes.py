from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import (
    LibraryCategory,
    LibraryLevel,
    LibrarySubject,
    LibraryResource,
    LibraryPurchase
)
from extensions import db

library_bp = Blueprint("library", __name__, url_prefix="/user/library")


# -------------------------
# Library Home → Redirect to Categories
# -------------------------
@library_bp.route("/", strict_slashes=False)
@login_required
def library_home():
    return redirect(url_for("library.show_categories"))


# -------------------------
# Show All Categories
# -------------------------
@library_bp.route("/categories/", strict_slashes=False)
@login_required
def show_categories():
    categories = LibraryCategory.query.order_by(LibraryCategory.name).all()
    return render_template("library/categories.html", categories=categories)


# -------------------------
# Show Levels for a Category
# -------------------------
@library_bp.route("/categories/<int:category_id>/levels/", strict_slashes=False)
@login_required
def show_levels(category_id):
    category = LibraryCategory.query.get_or_404(category_id)
    levels = LibraryLevel.query.filter_by(category_id=category.id).order_by(LibraryLevel.name).all()
    return render_template("library/levels.html", category=category, levels=levels)


# -------------------------
# Show Subjects for a Level
# -------------------------
@library_bp.route("/levels/<int:level_id>/subjects/", strict_slashes=False)
@login_required
def show_subjects(level_id):
    level = LibraryLevel.query.get_or_404(level_id)
    subjects = LibrarySubject.query.filter_by(level_id=level.id).order_by(LibrarySubject.name).all()
    return render_template("library/subjects.html", level=level, subjects=subjects)


# -------------------------
# Show Resources for a Subject
# -------------------------
@library_bp.route("/subjects/<int:subject_id>/resources/", strict_slashes=False)
@login_required
def show_resources(subject_id):
    resources = LibraryResource.query.filter_by(subject_id=subject_id).all()
    resource_list = []

    for idx, res in enumerate(resources):
        is_free = idx < 3 or res.is_free  # first 3 resources free placeholder
        purchased = False

        if not is_free and current_user.is_authenticated:
            purchased = LibraryPurchase.query.filter_by(
                user_id=current_user.id,
                resource_id=res.id
            ).first() is not None

        resource_list.append({
            "id": res.id,
            "title": res.title,
            "resource_type": res.resource_type,
            "file_url": res.file_url,
            "author": res.author,
            "can_access": is_free or purchased,
            "is_free": is_free,
            "price": res.price or 0.0
        })

    return render_template("library/resources.html", resources=resource_list)


# -------------------------
# Purchase a Paid Resource
# -------------------------
@library_bp.route("/resource/<int:resource_id>/purchase/", strict_slashes=False)
@login_required
def purchase_resource(resource_id):
    resource = LibraryResource.query.get_or_404(resource_id)

    existing_purchase = LibraryPurchase.query.filter_by(
        user_id=current_user.id,
        resource_id=resource.id
    ).first()

    if existing_purchase:
        flash("You already have access to this resource.")
        return redirect(url_for(
            "library.show_resources",
            subject_id=resource.subject_id
        ))

    if resource.is_free:
        flash("This resource is free. You can access it directly.")
        return redirect(url_for(
            "library.show_resources",
            subject_id=resource.subject_id
        ))

    purchase = LibraryPurchase(
        user_id=current_user.id,
        resource_id=resource.id,
        amount_paid=resource.price or 0.0
    )
    db.session.add(purchase)
    db.session.commit()

    flash(f"You have purchased {resource.title}.")
    return redirect(url_for(
        "library.show_resources",
        subject_id=resource.subject_id
    ))


# -------------------------
# Utility: Ensure placeholders for all levels and subjects
# -------------------------
def ensure_placeholders():
    categories = LibraryCategory.query.all()
    for cat in categories:
        levels = LibraryLevel.query.filter_by(category_id=cat.id).all()
        for lvl in levels:
            subjects = LibrarySubject.query.filter_by(level_id=lvl.id).all()
            for subj in subjects:
                resources = LibraryResource.query.filter_by(subject_id=subj.id).all()
                if len(resources) < 20:  # ensure at least 20 placeholder resources
                    for i in range(len(resources)+1, 21):
                        placeholder = LibraryResource(
                            title=f"{subj.name} Resource {i} (Placeholder)",
                            resource_type="pdf",
                            file_url="#",
                            author="TBA",
                            category_id=cat.id,
                            level_id=lvl.id,
                            subject_id=subj.id,
                            is_free=True
                        )
                        db.session.add(placeholder)
    db.session.commit()
