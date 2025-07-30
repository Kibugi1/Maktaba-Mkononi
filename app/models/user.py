from app.extensions import db
from datetime import datetime, timezone


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'librarian'
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    books_listed = db.relationship('Book', backref='listed_by_user', lazy=True)
    borrowings = db.relationship('Borrowing', backref='borrower', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100))
    genre = db.Column(db.String(100))
    description = db.Column(db.Text)
    listed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_available = db.Column(db.Boolean, default=True)
    listed_on = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    status = db.Column(db.String(20), default='pending') # 'pending', 'approved', 'rejected'

    borrowings = db.relationship('Borrowing', backref='book', lazy=True)

class Borrowing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    return_date = db.Column(db.DateTime)
    actual_returned_on = db.Column(db.DateTime, nullable=True)

    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    pickup_time = db.Column(db.String(100))               # e.g., "Monday 10am"
    pickup_location = db.Column(db.String(200))           # e.g., "Church office"
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    user = db.relationship('User', backref='notifications')
