from app import app, db
from models import Subject, LevelSubject, Resource

# Map of resources for subjects across JHS, SHS, Tertiary
# Real URLs for open/free content where available, otherwise placeholder
resources_data = {
    # -------------------------
    # JHS Subjects
    # -------------------------
    "Mathematics": [
        {"title": "Khan Academy Mathematics", "resource_type": "video", "file_url": "https://www.khanacademy.org/math"},
        {"title": "OpenStax Math PDF", "resource_type": "pdf", "file_url": "https://openstax.org/details/books/college-algebra"}
    ],
    "English Language": [
        {"title": "BBC Learning English", "resource_type": "video", "file_url": "https://www.bbc.co.uk/learningenglish"},
        {"title": "English Grammar PDF", "resource_type": "pdf", "file_url": "#"}
    ],
    "Integrated Science": [
        {"title": "Khan Academy Science", "resource_type": "video", "file_url": "https://www.khanacademy.org/science"},
    ],
    "Social Studies": [
        {"title": "Social Studies Intro PDF", "resource_type": "pdf", "file_url": "#"},
    ],
    "ICT": [
        {"title": "Introduction to Computers Video", "resource_type": "video", "file_url": "#"},
    ],
    "French": [
        {"title": "Learn French Video", "resource_type": "video", "file_url": "#"},
    ],
    "Religious & Moral Education": [
        {"title": "Religious Studies PDF", "resource_type": "pdf", "file_url": "#"},
    ],
    # -------------------------
    # SHS Subjects
    # -------------------------
    "Physics": [
        {"title": "Khan Academy Physics", "resource_type": "video", "file_url": "https://www.khanacademy.org/science/physics"},
    ],
    "Chemistry": [
        {"title": "Khan Academy Chemistry", "resource_type": "video", "file_url": "https://www.khanacademy.org/science/chemistry"},
    ],
    "Biology": [
        {"title": "Khan Academy Biology", "resource_type": "video", "file_url": "https://www.khanacademy.org/science/biology"},
    ],
    "Accounting": [
        {"title": "Accounting Basics PDF", "resource_type": "pdf", "file_url": "#"},
    ],
    "Business Management": [
        {"title": "Business Management Video", "resource_type": "video", "file_url": "#"},
    ],
    "Economics": [
        {"title": "Economics Open Textbook PDF", "resource_type": "pdf", "file_url": "#"},
    ],
    "History": [
        {"title": "World History Video", "resource_type": "video", "file_url": "#"},
    ],
    "Geography": [
        {"title": "Geography PDF", "resource_type": "pdf", "file_url": "#"},
    ],
    # -------------------------
    # Tertiary Subjects
    # -------------------------
    "Programming": [
        {"title": "Python Programming Free Video", "resource_type": "video", "file_url": "https://www.youtube.com/playlist?list=PLWKjhJtqVAbnUpXJNSB7oS2kA1DyUoKze"},
    ],
    "Data Structures": [
        {"title": "Data Structures PDF", "resource_type": "pdf", "file_url": "#"},
    ],
    "Database Systems": [
        {"title": "Database Systems Video", "resource_type": "video", "file_url": "#"},
    ],
    "Web Development": [
        {"title": "Web Development Free Video Series", "resource_type": "video", "file_url": "#"},
    ],
    "AI & Machine Learning": [
        {"title": "Intro to AI PDF", "resource_type": "pdf", "file_url": "#"},
    ],
}

with app.app_context():
    # Fetch all LevelSubject entries
    level_subjects = LevelSubject.query.all()

    for ls in level_subjects:
        subj_name = ls.subject.name

        # Get resources for this subject or fallback to placeholder
        subject_resources = resources_data.get(subj_name, [
            {"title": f"{subj_name} - Coming Soon", "resource_type": "pdf", "file_url": "#"}
        ])

        for res in subject_resources:
            resource = Resource(
                title=res["title"],
                resource_type=res["resource_type"],
                file_url=res["file_url"],
                level_subject_id=ls.id
            )
            db.session.add(resource)

    db.session.commit()
    print("✅ All resources seeded successfully!")
