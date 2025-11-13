from flask import Flask
from flask_login import LoginManager
from config import Config
from app.models import db, User

login_manager = LoginManager()

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)

    # Create tables
    with app.app_context():
        db.create_all()
        # Add sample books if database is empty
        from app.models import Book
        if Book.query.count() == 0:
            init_sample_data()

    return app

def init_sample_data():
    """Initialize database with sample books"""
    from app.models import Book, db

    sample_books = [
        Book(title="The Great Gatsby", author="F. Scott Fitzgerald",
             description="A classic American novel set in the Jazz Age",
             price=12.99, isbn="9780743273565", stock=15),
        Book(title="To Kill a Mockingbird", author="Harper Lee",
             description="A gripping tale of racial injustice and childhood innocence",
             price=14.99, isbn="9780061120084", stock=20),
        Book(title="1984", author="George Orwell",
             description="A dystopian social science fiction novel",
             price=13.99, isbn="9780451524935", stock=18),
        Book(title="Pride and Prejudice", author="Jane Austen",
             description="A romantic novel of manners",
             price=11.99, isbn="9780141439518", stock=12),
        Book(title="The Catcher in the Rye", author="J.D. Salinger",
             description="A story about teenage rebellion and alienation",
             price=13.49, isbn="9780316769488", stock=10),
        Book(title="The Hobbit", author="J.R.R. Tolkien",
             description="A fantasy novel and children's book",
             price=15.99, isbn="9780547928227", stock=25),
    ]

    for book in sample_books:
        db.session.add(book)
    db.session.commit()
