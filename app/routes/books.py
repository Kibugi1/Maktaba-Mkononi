from app.models import db, Book, Borrowing, Notification
from flask import  Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timezone

books = Blueprint('books', __name__)

@books.route('/books')
def all_books():
    books = Book.query.all()
    return render_template('books.html', books=books)

@books.route('/books/genre/<genre_name>')
def books_by_genre(genre_name):
    books = Book.query.filter_by(genre=genre_name).all()
    return render_template('books.html', books=books, genre=genre_name)

@books.route('/book/<int:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_details.html', book=book)

@books.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        description = request.form['description']

        new_book = Book(title=title, author=author, genre=genre, description=description, listed_by=session.get('user_id'))
        db.session.add(new_book)
        db.session.commit()

        flash('Book added successfully.', 'success')
        return redirect(url_for('books.all_books'))

    return render_template('add_book.html')

@books.route('/my_books')
def my_books():
    if 'user_id' not in session:
        flash('Please log in to view your listed books.', 'warning')
        return redirect(url_for('auth.login'))

    user_books = Book.query.filter_by(listed_by=session['user_id']).all()
    return render_template('my_books.html', books=user_books)

@books.route('/borrow/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    if 'user_id' not in session:
        flash('You need to log in to borrow books.', 'warning')
        return redirect(url_for('auth.login'))

    book = Book.query.get_or_404(book_id)
    if not book.is_available:
        flash('This book is currently unavailable.', 'danger')
        return redirect(url_for('books.all_books'))

    borrowing = Borrowing(book_id=book.id, borrower_id=session['user_id'])
    book.is_available = False
    db.session.add(borrowing)
    db.session.commit()

    flash('Book borrowed successfully.', 'success')
    return redirect(url_for('books.all_books'))

@books.route('/my_borrowed_books')
def my_borrowed_books():
    if 'user_id' not in session:
        flash('Please log in to view your borrowed books.', 'warning')
        return redirect(url_for('auth.login'))

    borrowed = Borrowing.query.filter_by(borrower_id=session['user_id']).all()
    return render_template('my_borrowed_books.html', borrowed_books=borrowed)

@books.route('/return/<int:book_id>', methods=['POST'])
def return_book(book_id):
    if 'user_id' not in session:
        flash('Login required.', 'warning')
        return redirect(url_for('auth.login'))

    borrowing = Borrowing.query.filter_by(book_id=book_id, borrower_id=session['user_id'], returned_at=None).first()
    if not borrowing:
        flash('Borrow record not found or already returned.', 'danger')
        return redirect(url_for('books.my_borrowed_books'))

    borrowing.returned_at = datetime.now(timezone.utc)
    book = Book.query.get(book_id)
    book.is_available = True

    db.session.commit()
    flash('Book returned successfully.', 'success')
    return redirect(url_for('books.my_borrowed_books'))

@books.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)

    if book.listed_by != session.get('user_id'):
        flash('Unauthorized.', 'danger')
        return redirect(url_for('books.my_books'))

    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.genre = request.form['genre']
        book.description = request.form['description']
        db.session.commit()

        flash('Book updated successfully.', 'success')
        return redirect(url_for('books.my_books'))

    return render_template('edit_book.html', book=book)

@books.route('/notifications')
def view_notifications():
    user_id = session.get('user_id')
    if not user_id:
        flash("Login required.")
        return redirect(url_for('auth.login'))

    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifications)


@books.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)

    if book.listed_by != session.get('user_id'):
        flash('Unauthorized.', 'danger')
        return redirect(url_for('books.my_books'))

    db.session.delete(book)
    db.session.commit()
    flash('Book deleted.', 'info')
    return redirect(url_for('books.my_books'))
