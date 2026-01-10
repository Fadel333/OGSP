from datetime import datetime, timedelta
import uuid
from flask_login import UserMixin
from extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

# =========================
# LOGIN LOADER
# =========================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =========================
# ASSOCIATION TABLES
# =========================
user_levels = db.Table(
    "user_levels",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("level_id", db.Integer, db.ForeignKey("levels.id"), primary_key=True)
)

# =========================
# USER MODEL
# =========================
class User(db.Model, UserMixin):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(120))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(150), default=None)

    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(100), nullable=True)
    reset_password_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

     # Admin details
    is_admin = db.Column(db.Boolean, default=False)

    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(100), nullable=True)
    reset_password_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    # Relationships
    levels = db.relationship(
        "Level",
        secondary=user_levels,
        backref=db.backref("users", lazy="dynamic")
    )
    memberships = db.relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    group_join_requests = db.relationship("GroupJoinRequest", back_populates="user", cascade="all, delete-orphan")
    notifications = db.relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    purchases = db.relationship("Purchase", back_populates="user", cascade="all, delete-orphan")
    library_purchases = db.relationship("LibraryPurchase", back_populates="user", cascade="all, delete-orphan")

    # =====================
    # PASSWORD METHODS
    # =====================
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # =====================
    # TOKEN METHODS
    # =====================
    def generate_email_verification_token(self):
        self.email_verification_token = str(uuid.uuid4())
        db.session.commit()
        return self.email_verification_token

    def generate_reset_token(self, expiry_minutes=30):
        self.reset_password_token = str(uuid.uuid4())
        self.reset_token_expiry = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        db.session.commit()
        return self.reset_password_token

    def touch(self):
        self.last_active = datetime.utcnow()
        db.session.commit()

    def get_primary_level(self):
        return self.levels[0] if self.levels else None

    def __repr__(self):
        return f"<User {self.username}>"

# =========================
# GROUPS
# =========================
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    join_requests = db.relationship("GroupJoinRequest", back_populates="group", cascade="all, delete-orphan")
    messages = db.relationship("DiscussionMessage", back_populates="group", cascade="all, delete-orphan")

class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    is_approved = db.Column(db.Boolean, default=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="memberships")
    group = db.relationship("Group", back_populates="members")

class GroupJoinRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="group_join_requests")
    group = db.relationship("Group", back_populates="join_requests")

class DiscussionMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    group = db.relationship("Group", back_populates="messages")
    user = db.relationship("User")

# =========================
# NOTIFICATIONS
# =========================
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="notifications")

# =========================
# COURSES & LEVELS
# =========================
class CourseCategory(db.Model):
    __tablename__ = "course_categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    courses = db.relationship("Course", back_populates="category", cascade="all, delete-orphan")

class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("course_categories.id"), nullable=False)

    category = db.relationship("CourseCategory", back_populates="courses")
    levels = db.relationship("Level", back_populates="course", cascade="all, delete-orphan")

class Level(db.Model):
    __tablename__ = "levels"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    order = db.Column(db.Integer)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    course = db.relationship("Course", back_populates="levels")
    level_subjects = db.relationship("LevelSubject", back_populates="level", cascade="all, delete-orphan")

class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject_type = db.Column(db.String(20))

class LevelSubject(db.Model):
    __tablename__ = "level_subjects"
    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer, db.ForeignKey("levels.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)

    level = db.relationship("Level", back_populates="level_subjects")
    subject = db.relationship("Subject")
    resources = db.relationship("Resource", back_populates="level_subject", cascade="all, delete-orphan")

# =========================
# RESOURCES & PURCHASES
# =========================
class Resource(db.Model):
    __tablename__ = "resources"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    resource_type = db.Column(db.String(50))
    file_url = db.Column(db.String(255))
    author = db.Column(db.String(100))
    is_free = db.Column(db.Boolean, default=True)
    price = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    level_subject_id = db.Column(db.Integer, db.ForeignKey("level_subjects.id"), nullable=False)

    level_subject = db.relationship("LevelSubject", back_populates="resources")
    purchases = db.relationship("Purchase", back_populates="resource", cascade="all, delete-orphan")

class Purchase(db.Model):
    __tablename__ = "purchases"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="purchases")
    resource = db.relationship("Resource", back_populates="purchases")

# =========================
# LIBRARY MODELS
# =========================
class LibraryCategory(db.Model):
    __tablename__ = "library_category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    levels = db.relationship("LibraryLevel", back_populates="category", cascade="all, delete-orphan")
    resources = db.relationship("LibraryResource", back_populates="category", cascade="all, delete-orphan")

class LibraryLevel(db.Model):
    __tablename__ = "library_level"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("library_category.id"), nullable=False)

    category = db.relationship("LibraryCategory", back_populates="levels")
    subjects = db.relationship("LibrarySubject", back_populates="level", cascade="all, delete-orphan")
    resources = db.relationship("LibraryResource", back_populates="level", cascade="all, delete-orphan")

class LibrarySubject(db.Model):
    __tablename__ = "library_subject"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey("library_level.id"), nullable=False)

    level = db.relationship("LibraryLevel", back_populates="subjects")
    resources = db.relationship("LibraryResource", back_populates="subject", cascade="all, delete-orphan")

class LibraryResource(db.Model):
    __tablename__ = "library_resource"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    resource_type = db.Column(db.String(50))
    file_url = db.Column(db.String(300), nullable=False)
    author = db.Column(db.String(120))
    is_free = db.Column(db.Boolean, default=True)
    price = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category_id = db.Column(db.Integer, db.ForeignKey("library_category.id"), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey("library_level.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("library_subject.id"), nullable=False)

    category = db.relationship("LibraryCategory", back_populates="resources")
    level = db.relationship("LibraryLevel", back_populates="resources")
    subject = db.relationship("LibrarySubject", back_populates="resources")
    purchases = db.relationship("LibraryPurchase", back_populates="resource", cascade="all, delete-orphan")

class LibraryPurchase(db.Model):
    __tablename__ = "library_purchase"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey("library_resource.id"), nullable=False)
    amount_paid = db.Column(db.Float, default=0.0)
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="library_purchases")
    resource = db.relationship("LibraryResource", back_populates="purchases")

# =========================
# QUIZZES
# =========================
class Quiz(db.Model):
    __tablename__ = "quiz"
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey("levels.id"), nullable=False)
    name = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subject = db.relationship("Subject")
    level = db.relationship("Level")
    questions = db.relationship("Question", back_populates="quiz", cascade="all, delete-orphan")

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # objective / theory
    correct_answer = db.Column(db.String(255), nullable=True)
    topic = db.Column(db.String(100))
    options = db.Column(db.Text)  # JSON string for objective questions

    quiz = db.relationship("Quiz", back_populates="questions")

class UserQuizAttempt(db.Model):
    __tablename__ = "user_quiz_attempt"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    score = db.Column(db.Float)
    grade = db.Column(db.String(20))
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Category {self.name}>"


# =========================
# BLOG
# =========================
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    image = db.Column(db.String(255), nullable=True)  # <-- new
    video = db.Column(db.String(255), nullable=True)  # <-- new
