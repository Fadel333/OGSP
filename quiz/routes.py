from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Quiz, Question, UserQuizAttempt, Subject, Level
import random

quiz_bp = Blueprint("quiz", __name__, url_prefix="/quiz")

# -------------------------
# START QUIZ (choose subject first)
# -------------------------
@quiz_bp.route("/", methods=["GET"])
@login_required
def start():
    # get user's level (assume first course for simplicity)
    level = current_user.levels[0]  # customize as per your model
    subjects = Subject.query.all()  # filter subjects by user level
    return render_template("quiz/start.html", subjects=subjects)

# -------------------------
# LOAD QUIZ QUESTIONS
# -------------------------
@quiz_bp.route("/take/<int:subject_id>", methods=["GET", "POST"])
@login_required
def take(subject_id):
    # get user's level
    level = current_user.levels[0]
    quiz = Quiz.query.filter_by(subject_id=subject_id, level_id=level.id).first()
    if not quiz:
        flash("Quiz not available for this subject yet.", "error")
        return redirect(url_for("quiz.start"))

    if request.method == "POST":
        total_score = 0
        for q in quiz.questions:
            ans = request.form.get(f"question_{q.id}")
            if q.type == "objective" and ans.strip().lower() == q.correct_answer.strip().lower():
                total_score += 1
            # For theory, you can extend with partial scoring if needed

        # calculate percentage
        score_percentage = (total_score / len(quiz.questions)) * 100
        grade = ""
        if score_percentage >= 90:
            grade = "Excellent"
        elif score_percentage >= 75:
            grade = "Good"
        elif score_percentage >= 60:
            grade = "Average"
        elif score_percentage >= 50:
            grade = "Pass"
        else:
            grade = "Fail"

        # save attempt
        attempt = UserQuizAttempt(
            user_id=current_user.id,
            quiz_id=quiz.id,
            score=score_percentage,
            grade=grade
        )
        db.session.add(attempt)
        db.session.commit()

        if grade == "Fail":
            flash("You failed. Try similar questions again.", "error")
            return redirect(url_for("quiz.take", subject_id=subject_id))

        flash(f"Quiz completed! Grade: {grade}", "success")
        return redirect(url_for("dashboard.dashboard"))

    # GET: randomize 30 objective and 20 theory questions
    objective_questions = [q for q in quiz.questions if q.type=="objective"]
    theory_questions = [q for q in quiz.questions if q.type=="theory"]

    selected_objectives = random.sample(objective_questions, min(30, len(objective_questions)))
    selected_theory = random.sample(theory_questions, min(20, len(theory_questions)))

    questions_to_show = selected_objectives + selected_theory
    random.shuffle(questions_to_show)

    return render_template("quiz/take.html", questions=questions_to_show)
