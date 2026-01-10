from app import create_app, db
from models import Course, Level, Subject, LevelSubject, Quiz, Question
import random
import json

app = create_app()

with app.app_context():
    print("Seeding quizzes for all subjects...")

    # Dummy topics
    dummy_topics = ["Topic A", "Topic B", "Topic C", "Topic D", "Topic E"]

    # Loop through all level-subject combinations
    for ls in LevelSubject.query.all():
        level = ls.level
        subject = ls.subject

        # Skip if quiz already exists
        if Quiz.query.filter_by(level_id=level.id, subject_id=subject.id).first():
            continue

        # Create a new quiz for this subject and level
        quiz = Quiz(level_id=level.id, subject_id=subject.id, name=f"{subject.name} Quiz")
        db.session.add(quiz)
        db.session.commit()  # Commit to get quiz.id

        # Create 30 objective questions
        for i in range(30):
            topic = random.choice(dummy_topics)
            question_text = f"{subject.name} - {topic} - Objective Question {i+1}"
            options = ["A", "B", "C", "D"]
            correct_answer = random.choice(options)
            q = Question(
                quiz_id=quiz.id,
                text=question_text,
                type="objective",
                options=json.dumps(options),
                correct_answer=correct_answer,
                topic=topic
            )
            db.session.add(q)

        # Create 20 theory questions
        for i in range(20):
            topic = random.choice(dummy_topics)
            question_text = f"{subject.name} - {topic} - Theory Question {i+1}"
            q = Question(
                quiz_id=quiz.id,
                text=question_text,
                type="theory",
                topic=topic
            )
            db.session.add(q)

    # Commit all questions
    db.session.commit()
    print("✅ Quiz seeding complete!")
