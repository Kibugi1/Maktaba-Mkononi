from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import db, User, Book, Borrowing
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/')
def home():
    return redirect(url_for('main.login'))

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
        return redirect(url_for('main.login'))
    
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

            if user.role == 'librarian':
                return redirect(url_for('main.dashboard', role='librarian'))
            else:
                return redirect(url_for('main.dashboard', role='user'))
        
        flash('Invalid credentials.', 'danger')

    return render_template('login.html')

@auth.route('/dashboard/<role>')
def dashboard(role):
    if session.get('user_role') != role:
        flash('Unauthorized', 'warning')
        return redirect(url_for('main.login'))
    return render_template('dashboard.html', role=role)

@auth.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('auth.login'))
