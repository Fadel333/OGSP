# dashboard_bp.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import os

from extensions import db
from models import User, GroupMember, Group, Course, DiscussionMessage, LibraryPurchase, Resource, Notification

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def dashboard():
    # Live counts
    groups_count = GroupMember.query.filter_by(user_id=current_user.id).count()
    courses_count = Course.query.count()
    members_count = User.query.count()
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    library_purchases_count = LibraryPurchase.query.filter_by(user_id=current_user.id).count()
    recent_resources_count = Resource.query.order_by(Resource.created_at.desc()).limit(5).count()

    # Online users (active within last 5 minutes)
    online_users = User.query.filter(User.last_active >= datetime.utcnow() - timedelta(minutes=5)).all()

    # Recent activity feed (last 5 discussion messages)
    recent_messages = DiscussionMessage.query.order_by(DiscussionMessage.timestamp.desc()).limit(5).all()
    activities = [
        f"{msg.user.username} posted in {msg.group.name}" for msg in recent_messages
    ]

    # Recently joined groups
    recent_groups = Group.query.join(GroupMember).filter(GroupMember.user_id == current_user.id)\
                         .order_by(GroupMember.joined_at.desc()).limit(5).all()

    # Featured courses placeholder
    featured_courses = Course.query.limit(4).all()

    return render_template(
        'auth/dashboard.html',
        groups_count=groups_count,
        courses_count=courses_count,
        members_count=members_count,
        unread_notifications=unread_notifications,
        library_purchases_count=library_purchases_count,
        recent_resources_count=recent_resources_count,
        online_users=online_users,
        activities=activities,
        recent_groups=recent_groups,
        featured_courses=featured_courses,
        current_user=current_user
    )

@dashboard_bp.route('/upload-profile', methods=['POST'])
@login_required
def upload_profile():
    if 'profile_pic' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('dashboard.dashboard'))
    
    file = request.files['profile_pic']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('dashboard.dashboard'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_pics')
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))
        current_user.profile_pic = filename
        current_user.last_active = datetime.utcnow()  # update last active on profile change
        db.session.commit()
        flash('Profile picture updated successfully!', 'success')
    else:
        flash('Invalid file type. Allowed types: png, jpg, jpeg, gif', 'error')
    
    return redirect(url_for('dashboard.dashboard'))
