from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import db, User, Book, Borrowing, Notification
from datetime import datetime, timedelta, timezone
from functools import  wraps
from flask_login import login_required

auth = Blueprint('auth', __name__)

# Login required decorator to protect the routes
def login_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for('auth.login'))
            if role and session.get('user_role') != role:
                flash("Access denied.", "danger")
                return redirect(url_for('auth.login'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@auth.route('/')
def home():
    return redirect(url_for('index.html'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'user')

        hashed_password = generate_password_hash(password)
        new_user = User(full_name=name, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login.html'))
    
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_role'] = user.role
            flash('Login successful.', 'success')

          # Redirect based on role using route name, not template
            return redirect(url_for('auth.dashboard', role=user.role))

        flash('Invalid credentials.', 'danger')

    return render_template('login.html')

@auth.route('/dashboard/<role>')
def dashboard(role):
    user_id = session.get('user_id')
    user_role = session.get('user_role')

    if user_role != role:
        flash('Unauthorized access.', 'warning')
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)

    if role == 'librarian':
        # Librarian-specific data
        pending_books = Book.query.filter_by(status='pending').all()
        borrow_requests = Borrowing.query.filter_by(status='pending').all()
        approved_returns = Borrowing.query.filter(
            Borrowing.status == 'approved',
            Borrowing.actual_returned_on.isnot(None)
        ).all()
        all_users = User.query.filter(User.role != 'librarian').all()

        return render_template('librariandashboard.html',
            user=user,
            pending_books=pending_books,
            borrow_requests=borrow_requests,
            returned_books=approved_returns,
            users=all_users
        )

    elif role == 'user':
        # User-specific data
        now = datetime.now(timezone.utc)
        user_books = Book.query.filter_by(listed_by=user_id, status='approved').all()
        borrowed_books = Borrowing.query.filter_by(borrower_id=user_id, status='approved').all()

        due_soon_count = sum(
            1 for b in borrowed_books
            if b.return_date and now <= b.return_date <= now + timedelta(days=3)
        )

        overdue_count = sum(
            1 for b in borrowed_books
            if b.return_date and b.return_date < now and not b.actual_returned_on
        )

        notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(5).all()

        explore_books = Book.query.filter(
            Book.is_available == True,
            Book.status == 'approved',
            Book.listed_by != user_id
        ).all()

        return render_template('userdashboard.html',
            user=user,
            user_books=user_books,
            borrowed_books=borrowed_books,
            notifications=notifications,
            due_soon_count=due_soon_count,
            overdue_count=overdue_count,
            explore_books=explore_books,
            current_time=now
        )

    else:
        flash('Unknown role.', 'danger')
        return redirect(url_for('auth.login'))


@auth.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('auth.login'))
