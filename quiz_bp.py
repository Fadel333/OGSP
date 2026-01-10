from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Course, Level, Subject, Quiz, Question, UserQuizAttempt
from extensions import db
import random, json

quiz_bp = Blueprint("quiz", __name__, url_prefix="/quiz")

# -------------------------
# STEP 1: Courses
# -------------------------
@quiz_bp.route("/")
@login_required
def courses():
    courses = Course.query.all()
    return render_template("quiz/courses.html", courses=courses)

# -------------------------
# STEP 2: Levels for selected course
# -------------------------
@quiz_bp.route("/level/<int:course_id>")
@login_required
def levels(course_id):
    levels = Level.query.filter_by(course_id=course_id).all()
    return render_template("quiz/levels.html", levels=levels, course_id=course_id)

# -------------------------
# STEP 3: Subjects for selected level
# -------------------------
@quiz_bp.route("/subject/<int:level_id>")
@login_required
def subjects(level_id):
    subjects = Subject.query.join(Quiz).filter(Quiz.level_id==level_id).all()
    return render_template("quiz/subjects.html", subjects=subjects, level_id=level_id)

# -------------------------
# STEP 4: Topics in the subject
# -------------------------
@quiz_bp.route("/topic/<int:subject_id>")
@login_required
def topics(subject_id):
    quiz = Quiz.query.filter_by(subject_id=subject_id).first()
    if not quiz:
        flash("No quiz available for this subject.", "error")
        return redirect(url_for("quiz.subjects", level_id=current_user.levels[0].id))
    
    topics = sorted(set([q.topic for q in quiz.questions]))
    return render_template("quiz/topics.html", topics=topics, subject_id=subject_id)

# -------------------------
# STEP 5: Question type selection for a topic
# -------------------------
@quiz_bp.route("/type/<int:subject_id>/<qtype>/<topic>")
@login_required
def question_type(subject_id, qtype, topic):
    quiz = Quiz.query.filter_by(subject_id=subject_id).first()
    if not quiz:
        flash("Quiz not available.", "error")
        return redirect(url_for("quiz.subjects", level_id=current_user.levels[0].id))
    
    # Filter by type and topic
    questions = [q for q in quiz.questions if q.type == qtype and q.topic == topic]

    for q in questions:
        if q.type=="objective" and q.options:
            try:
                q.options_list = json.loads(q.options)
            except:
                q.options_list = []

    return render_template("quiz/take.html", questions=questions, qtype=qtype, subject_id=subject_id, topic=topic)

# -------------------------
# STEP 6: Submit answers & auto-grade
# -------------------------
@quiz_bp.route("/submit/<int:subject_id>/<topic>/<qtype>", methods=["POST"])
@login_required
def submit(subject_id, topic, qtype):
    quiz = Quiz.query.filter_by(subject_id=subject_id).first()
    if not quiz:
        flash("Quiz not available.", "error")
        return redirect(url_for("quiz.subjects", level_id=current_user.levels[0].id))

    total_score = 0
    # Filter by topic and type
    relevant_questions = [q for q in quiz.questions if q.type==qtype and q.topic==topic]
    
    for q in relevant_questions:
        ans = request.form.get(f"question_{q.id}")
        if q.type=="objective" and ans and ans.strip().lower()==(q.correct_answer or "").strip().lower():
            total_score += 1

    # Calculate percentage
    score_percent = (total_score/len(relevant_questions)*100) if relevant_questions else 0

    # Grade
    if score_percent >= 90: grade="Excellent"
    elif score_percent >= 75: grade="Good"
    elif score_percent >= 60: grade="Average"
    elif score_percent >= 50: grade="Pass"
    else: grade="Fail"

    # Save attempt
    attempt = UserQuizAttempt(user_id=current_user.id, quiz_id=quiz.id, score=score_percent, grade=grade)
    db.session.add(attempt)
    db.session.commit()

    flash(f"Quiz completed! Grade: {grade}", "success")
    return redirect(url_for("quiz.courses"))
