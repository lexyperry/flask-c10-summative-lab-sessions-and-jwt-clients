# Import necessary modules and objects
from app import app
from models import db, User, Book
from faker import Faker

fake = Faker()

# Start the app context so database operations can run
with app.app_context():
    print("Seeding database...")

    # Clear existing records to avoid duplicates
    Book.query.delete()
    User.query.delete()

    # Create a test user
    user = User(username="testuser")
    user.password_hash = "password123"# Password will be hashed via setter
    db.session.add(user)
    db.session.commit()# Commit to generate the user ID

    # Create 10 fake book entries for the test user
    for _ in range(10):
        book = Book(
            title=fake.sentence(nb_words=3),# Random short title
            author=fake.name(), # Random author name
            rating=fake.random_int(min=1, max=5), # Random rating between 1-5
            user_id=user.id #Associate book with user
        )
        db.session.add(book)

    db.session.commit()
    print("Done seeding!")
