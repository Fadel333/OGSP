from app import create_app, db
from models import (
    CourseCategory, Course, Level, Subject, LevelSubject, Resource,
    LibraryCategory, LibraryLevel, LibrarySubject, LibraryResource
)
from datetime import datetime

app = create_app()

with app.app_context():
    print("Seeding courses, levels, and subjects...")

    # -------------------------
    # Courses, Levels, Subjects
    # -------------------------
    courses_data = {
        "JHS": {
            "General": [
                ("Mathematics", "core"), ("English Language", "core"),
                ("Integrated Science", "core"), ("Social Studies", "core"),
                ("ICT", "core"), ("French", "elective"),
                ("Religious & Moral Education", "elective"), ("Arts", "elective"),
                ("Agriculture", "elective"), ("Business Basics", "elective")
            ],
            "Science": [
                ("Mathematics", "core"), ("Physics", "core"), ("Chemistry", "core"),
                ("Biology", "core"), ("Integrated Science", "core"),
                ("ICT", "elective"), ("English Language", "core")
            ],
            "Arts": [
                ("Literature", "core"), ("History", "core"), ("Geography", "core"),
                ("Arts", "elective"), ("French", "elective"),
                ("Religious & Moral Education", "elective"), ("English Language", "core")
            ],
            "Business": [
                ("Economics", "core"), ("Business Basics", "core"), ("Accounting Basics", "core"),
                ("Mathematics", "core"), ("ICT", "elective"), ("English Language", "core")
            ]
        },
        "SHS": {
            "General Science": [
                ("Mathematics", "core"), ("Physics", "core"), ("Chemistry", "core"),
                ("Biology", "core"), ("Elective Science", "elective"),
                ("English Language", "core"), ("Economics", "elective"),
                ("Business Management", "elective"), ("History", "elective"),
                ("Computer Science", "elective")
            ],
            "Business": [
                ("Accounting", "core"), ("Economics", "core"), ("Business Management", "core"),
                ("Mathematics", "core"), ("ICT", "elective"), ("Finance", "elective"),
                ("English Language", "core")
            ],
            "Arts": [
                ("Literature", "core"), ("History", "core"), ("Geography", "core"),
                ("Economics", "elective"), ("Arts", "elective"),
                ("Political Science", "elective"), ("English Language", "core")
            ],
            "Technical": [
                ("Technical Drawing", "core"), ("Engineering Basics", "core"),
                ("Mathematics", "core"), ("Physics", "core"),
                ("ICT", "elective"), ("Computer Science", "elective")
            ]
        },
        "Tertiary": {
            "Computer Science / IT": [
                ("Programming", "core"), ("Data Structures", "core"),
                ("Database Systems", "core"), ("Web Development", "core"),
                ("AI & Machine Learning", "elective"), ("Cybersecurity", "elective"),
                ("Networking", "elective"), ("Computer Graphics", "elective"),
                ("Mathematics", "core"), ("Software Engineering", "core")
            ],
            "Business Administration": [
                ("Accounting", "core"), ("Finance", "core"), ("Marketing", "core"),
                ("Economics", "core"), ("Business Law", "elective"),
                ("Management", "elective"), ("HR Management", "elective"),
                ("Operations Management", "elective"), ("Entrepreneurship", "elective")
            ],
            "Law": [
                ("Constitutional Law", "core"), ("Criminal Law", "core"),
                ("Contract Law", "core"), ("International Law", "elective"),
                ("Political Science", "elective"), ("Economics", "elective")
            ],
            "Engineering": [
                ("Engineering Mechanics", "core"), ("Thermodynamics", "core"),
                ("Electrical Circuits", "core"), ("Mathematics", "core"),
                ("Computer-Aided Design", "elective"), ("Fluid Mechanics", "core"),
                ("Materials Science", "core"), ("Electronics", "elective")
            ]
        }
    }

    for category_name, courses in courses_data.items():
        category = CourseCategory.query.filter_by(name=category_name).first()
        if not category:
            category = CourseCategory(name=category_name)
            db.session.add(category)
            db.session.commit()

        for course_name, subjects_list in courses.items():
            course = Course.query.filter_by(name=course_name, category_id=category.id).first()
            if not course:
                course = Course(name=course_name, category=category)
                db.session.add(course)
                db.session.commit()

            # Levels
            level_count = 3 if category_name in ["JHS", "SHS"] else 4
            levels = []
            for i in range(1, level_count + 1):
                level_name = f"{category_name} {i}" if category_name != "Tertiary" else f"{course_name} Year {i}"
                level = Level.query.filter_by(name=level_name, course_id=course.id).first()
                if not level:
                    level = Level(name=level_name, order=i, course=course)
                    db.session.add(level)
                levels.append(level)
            db.session.commit()

            # Subjects
            subjects = []
            for subj_name, subj_type in subjects_list:
                subj = Subject.query.filter_by(name=subj_name).first()
                if not subj:
                    subj = Subject(name=subj_name, subject_type=subj_type)
                    db.session.add(subj)
                    db.session.commit()
                subjects.append(subj)

            # LevelSubjects
            for level in levels:
                for subj in subjects:
                    exists = LevelSubject.query.filter_by(level_id=level.id, subject_id=subj.id).first()
                    if not exists:
                        db.session.add(LevelSubject(level=level, subject=subj))
            db.session.commit()

            # -------------------------
            # Create 20 placeholder resources per subject
            # -------------------------
            for level in levels:
                for subj in subjects:
                    level_subject = LevelSubject.query.filter_by(level_id=level.id, subject_id=subj.id).first()
                    for i in range(1, 21):
                        title = f"{subj.name} - Resource {i}"
                        exists = Resource.query.filter_by(title=title, level_subject_id=level_subject.id).first()
                        if not exists:
                            resource = Resource(
                                title=title,
                                resource_type="pdf" if i % 2 == 0 else "video",
                                file_url="#",
                                author="Placeholder Author",
                                level_subject=level_subject,
                                is_free=True
                            )
                            db.session.add(resource)
            db.session.commit()

    print("✅ Courses, levels, subjects, and placeholder resources seeded successfully!")

    # -------------------------
    # Library seeding (unchanged)
    # -------------------------
    print("Library remains untouched.")
