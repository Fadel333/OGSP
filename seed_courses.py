from app import app, db
from models import CourseCategory, Course, Level, Subject, LevelSubject

# All West African courses
courses_data = {
    "JHS": {
        "General": [
            ("Mathematics", "core"),
            ("English Language", "core"),
            ("Integrated Science", "core"),
            ("Social Studies", "core"),
            ("ICT", "core"),
            ("French", "elective"),
            ("Religious & Moral Education", "elective")
        ],
        "Technical/Vocational": [
            ("Basic Electronics", "core"),
            ("Woodwork", "core"),
            ("Metalwork", "core"),
            ("Agriculture", "core"),
            ("Home Economics", "elective")
        ]
    },
    "SHS": {
        "General Science": [
            ("Mathematics", "core"),
            ("Physics", "core"),
            ("Chemistry", "core"),
            ("Biology", "core"),
            ("Elective Science", "elective")
        ],
        "Business": [
            ("Accounting", "core"),
            ("Business Management", "core"),
            ("Economics", "core"),
            ("Commerce", "core"),
            ("Entrepreneurship", "elective")
        ],
        "Arts": [
            ("History", "core"),
            ("Geography", "core"),
            ("Literature", "core"),
            ("Government", "core"),
            ("Fine Arts", "elective")
        ],
        "Technical": [
            ("Electrical Technology", "core"),
            ("Mechanical Technology", "core"),
            ("Auto Mechanics", "core"),
            ("Woodwork", "core"),
            ("Metalwork", "elective")
        ],
        "Home Economics": [
            ("Food & Nutrition", "core"),
            ("Clothing & Textiles", "core"),
            ("Management in Living", "core"),
            ("Home Management", "elective")
        ],
        "Visual Arts": [
            ("Drawing & Painting", "core"),
            ("Sculpture", "core"),
            ("Textile Design", "core"),
            ("Ceramics", "elective")
        ],
        "Agricultural Science": [
            ("Crop Science", "core"),
            ("Animal Husbandry", "core"),
            ("Fisheries", "core"),
            ("Soil Science", "elective")
        ],
        "General Arts": [
            ("Philosophy", "core"),
            ("Religion", "core"),
            ("Economics", "core"),
            ("Literature", "core"),
            ("History", "elective")
        ]
    },
    "Tertiary": {
        "Computer Science / IT": [
            ("Programming", "core"),
            ("Data Structures", "core"),
            ("Database Systems", "core"),
            ("Web Development", "core"),
            ("AI & Machine Learning", "elective")
        ],
        "Business / Economics": [
            ("Accounting", "core"),
            ("Economics", "core"),
            ("Finance", "core"),
            ("Business Management", "core"),
            ("Marketing", "elective")
        ],
        "Engineering": [
            ("Mathematics", "core"),
            ("Physics", "core"),
            ("Engineering Mechanics", "core"),
            ("Electrical Circuits", "core"),
            ("Thermodynamics", "elective")
        ],
        "Medicine & Health Sciences": [
            ("Anatomy", "core"),
            ("Physiology", "core"),
            ("Biochemistry", "core"),
            ("Pharmacology", "core"),
            ("Medical Ethics", "elective")
        ],
        "Arts & Humanities": [
            ("History", "core"),
            ("Philosophy", "core"),
            ("Literature", "core"),
            ("Political Science", "core"),
            ("Sociology", "elective")
        ],
        "Law": [
            ("Constitutional Law", "core"),
            ("Criminal Law", "core"),
            ("Contract Law", "core"),
            ("Property Law", "core"),
            ("International Law", "elective")
        ]
    }
}

with app.app_context():
    for category_name, courses in courses_data.items():
        # 1️⃣ Create category
        category = CourseCategory.query.filter_by(name=category_name).first()
        if not category:
            category = CourseCategory(name=category_name)
            db.session.add(category)
            db.session.commit()

        for course_name, subjects_list in courses.items():
            # 2️⃣ Create course
            course = Course.query.filter_by(name=course_name, category_id=category.id).first()
            if not course:
                course = Course(name=course_name, category=category)
                db.session.add(course)
                db.session.commit()

            # 3️⃣ Create levels
            if category_name in ["JHS", "SHS"]:
                level_count = 3
            else:
                level_count = 4  # Tertiary years

            levels = []
            for i in range(1, level_count + 1):
                level_name = f"{category_name} {i}" if category_name != "Tertiary" else f"{course_name} Year {i}"
                level = Level.query.filter_by(name=level_name, course_id=course.id).first()
                if not level:
                    level = Level(name=level_name, order=i, course=course)
                    db.session.add(level)
                levels.append(level)
            db.session.commit()

            # 4️⃣ Create subjects
            subjects = []
            for subj_name, subj_type in subjects_list:
                subj = Subject.query.filter_by(name=subj_name).first()
                if not subj:
                    subj = Subject(name=subj_name, subject_type=subj_type)
                    db.session.add(subj)
                    db.session.commit()
                subjects.append(subj)

            # 5️⃣ Assign subjects to levels
            for level in levels:
                for subj in subjects:
                    exists = LevelSubject.query.filter_by(level_id=level.id, subject_id=subj.id).first()
                    if not exists:
                        level_subj = LevelSubject(level=level, subject=subj)
                        db.session.add(level_subj)
            db.session.commit()

    print("✅ All JHS, SHS, and Tertiary courses, levels, and subjects seeded successfully!")
