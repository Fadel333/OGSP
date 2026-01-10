from app import create_app
from extensions import db
from models import LibraryCategory, LibraryLevel, LibrarySubject, LibraryResource

app = create_app()
app.app_context().push()

# -----------------
# Add categories
# -----------------
literature = LibraryCategory(name="Literature")
history = LibraryCategory(name="History")
poems = LibraryCategory(name="Poems")

db.session.add_all([literature, history, poems])
db.session.commit()

# -----------------
# Add levels
# -----------------
jhs = LibraryLevel(name="JHS")
shs = LibraryLevel(name="SHS")
tertiary = LibraryLevel(name="Tertiary")

db.session.add_all([jhs, shs, tertiary])
db.session.commit()

# -----------------
# Add subjects
# -----------------
english = LibrarySubject(name="English")
ghana_history = LibrarySubject(name="Ghana History")
world_history = LibrarySubject(name="World History")

db.session.add_all([english, ghana_history, world_history])
db.session.commit()

# -----------------
# Add resources
# -----------------
book1 = LibraryResource(
    title="Classic English Literature",
    resource_type="pdf",
    file_url="static/library/classic_english.pdf",
    author="John Smith",
    category=literature,
    level=jhs,
    subject=english,
    is_free=True
)

video1 = LibraryResource(
    title="Ghana History Documentary",
    resource_type="video",
    file_url="static/library/ghana_history.mp4",
    author="History Channel",
    category=history,
    level=shs,
    subject=ghana_history,
    is_free=True
)

db.session.add_all([book1, video1])
db.session.commit()

print("Library seeded successfully!")
