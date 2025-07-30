from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import db, Book, Borrowing, Notification
from datetime import datetime

librarian = Blueprint('librarian', __name__, url_prefix='/librarian')

# Require librarian role
def librarian_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('user_role') != 'librarian':
            flash("Access denied. Librarian only.", 'danger')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return wrapper

@librarian.route('/all_books')
@librarian_required
def all_books():
    books = Book.query.order_by(Book.listed_on.desc()).all()
    return render_template('librarian/all_books.html', books=books)

# View pending book listings
@librarian.route('/pending_books')
@librarian_required
def pending_books():
    books = Book.query.filter_by(status='pending').all()
    return render_template('librarian/pending_books.html', books=books)

# Approve a book
@librarian.route('/approve_book/<int:book_id>')
@librarian_required
def approve_book(book_id):
    book = Book.query.get_or_404(book_id)
    book.status = 'approved'
    db.session.commit()

    flash('Book approved successfully.', 'success')
    return redirect(url_for('librarian.pending_books'))

# Delete a book
@librarian.route('/delete_book/<int:book_id>')
@librarian_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()

    flash('Book deleted successfully.', 'info')
    return redirect(url_for('librarian.pending_books'))

# View pending borrow requests
@librarian.route('/borrow_requests')
@librarian_required
def borrow_requests():
    requests = Borrowing.query.filter_by(status='pending').all()
    return render_template('librarian/borrow_requests.html', requests=requests)

# Approve borrow request
@librarian.route('/approve_borrow/<int:request_id>', methods=['POST'])
@librarian_required
def approve_borrow(request_id):
    request_data = Borrowing.query.get_or_404(request_id)
    pickup_time = request.form['pickup_time']
    pickup_location = request.form['pickup_location']

    request_data.status = 'approved'
    request_data.pickup_time = pickup_time
    request_data.pickup_location = pickup_location
    request_data.book.is_available = False

    # Notify the borrower
    message = f"Your request for '{request_data.book.title}' has been approved. Pick up at {pickup_location} on {pickup_time}."
    notification = Notification(user_id=request_data.borrower_id, message=message)
    db.session.add(notification)
    db.session.commit()

    flash('Borrow request approved and notification sent.', 'success')
    return redirect(url_for('librarian.borrow_requests'))

# Reject borrow request
@librarian.route('/reject_borrow/<int:request_id>')
@librarian_required
def reject_borrow(request_id):
    request_data = Borrowing.query.get_or_404(request_id)
    request_data.status = 'rejected'

    message = f"Your borrow request for '{request_data.book.title}' has been rejected."
    notification = Notification(user_id=request_data.borrower_id, message=message)
    db.session.add(notification)
    db.session.commit()

    flash('Borrow request rejected and user notified.', 'warning')
    return redirect(url_for('librarian.borrow_requests'))

@librarian.route('/mark_returned/<int:borrow_id>')
@librarian_required
def mark_as_returned(borrow_id):
    borrow = Borrowing.query.get_or_404(borrow_id)
    borrow.actual_returned_on = datetime.now()
    borrow.book.is_available = True
    db.session.commit()

    flash('Book marked as returned.', 'info')
    return redirect(url_for('librarian.borrow_requests'))

@librarian.route('/returned_books')
@librarian_required
def returned_books():
    borrows = Borrowing.query.filter(Borrowing.status == 'approved', Borrowing.actual_returned_on.isnot(None)).all()
    return render_template('librariandashboard.html', borrows=borrows)


@librarian.route('/notify_user/<int:user_id>', methods=['POST'])
@librarian_required
def notify_user(user_id):
    message = request.form['message']
    notification = Notification(user_id=user_id, message=message)
    db.session.add(notification)
    db.session.commit()
    
    flash('Notification sent.', 'success')
    return redirect(url_for('librarian.all_users'))

@librarian.route('/users')
@librarian_required
def all_users():
    users = User.query.filter(User.role != 'librarian').all()
    return render_template('librarian/users.html', users=users)
