from app.models import db, Book, Borrowing
from flask import  Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime

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
        return redirect(url_for('main.all_books'))

    return render_template('add_book.html')

@books.route('/borrow/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    if 'user_id' not in session:
        flash('You need to log in to borrow books.', 'warning')
        return redirect(url_for('books.login'))

    book = Book.query.get_or_404(book_id)
    if not book.is_available:
        flash('This book is currently unavailable.', 'danger')
        return redirect(url_for('books.all_books'))

    borrowing = Borrowing(book_id=book.id, borrower_id=session['user_id'])
    book.is_available = False
    db.session.add(borrowing)
    db.session.commit()

    flash('Book borrowed successfully.', 'success')
    return redirect(url_for('main.all_books'))
