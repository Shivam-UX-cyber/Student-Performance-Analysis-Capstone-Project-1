# app.py
from flask import Flask, render_template, request, redirect, url_for, session,flash
from datetime import timedelta
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random
from datetime import datetime
from flask import abort
from dotenv import load_dotenv
import os

# Initialize Flask app
app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=30)
load_dotenv()  # This loads variables from .env into environment
SECRET_KEY = os.getenv('SECRET_KEY')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

# SQLAlchemy config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Flask-Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')              # Ensure these are set in your .env file
mail = Mail(app)

class UserLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='logs')  # <-- Add this line

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Add this line

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html',gray_bg=True)

@app.route('/docs')
def docs():
    return render_template('docs.html',gray_bg=True)

@app.route('/support', methods=['GET', 'POST'])
def support():
    if request.method == 'POST':
        email = request.form.get('support-email')
        message = request.form.get('support-message')
        try:
            msg = Message(
                subject="Support Request from Student Performance Analysis",
                sender=app.config['MAIL_USERNAME'],
                recipients=['kumarshivambgs@gmail.com'],  # Where you want to receive support requests
                reply_to=email
            )
            msg.body = f"Support request from: {email}\n\nMessage:\n{message}"
            mail.send(msg)
            flash("Thank you for contacting support! We'll get back to you soon.", "success")
        except Exception as e:
            flash(f"Error sending support request: {e}", "error")
        return redirect(url_for('support'))
    return render_template('support.html',gray_bg=True)

@app.route('/learn_more')
def learn_more():
    return render_template('learn_more.html',gray_bg=True)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        session.permanent = True
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            otp = str(random.randint(100000, 999999))
            session['otp'] = otp
            session['name'] = user.name
            session['email'] = user.email

            # Send OTP email
            msg = Message('Your OTP Code', sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f'Your OTP code is {otp}'
            try:
                mail.send(msg)
            except Exception as e:
                flash(f"Error sending OTP email: {e}", "error")
                return redirect(url_for('signin'))

            return redirect(url_for('verify_otp'))
        else:
            flash("Invalid email or password. Please try again.", "error")
            return redirect(url_for('signin'))
    return render_template('signin.html', hide_signin_btn=True)

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        if user_otp == session.get('otp'):
            # Log the login event
            user = User.query.filter_by(email=session.get('email')).first()
            if user:
                log = UserLog(user_id=user.id)
                db.session.add(log)
                db.session.commit()
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid OTP. Please try again.", "error")
            return redirect(url_for('verify_otp'))
    return render_template('verify_otp.html')

@app.route('/verify_signup_otp', methods=['GET', 'POST'])
def verify_signup_otp():
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        if user_otp == session.get('signup_otp'):
            # Save user info to database
            new_user = User(
                name=session.get('signup_name'),
                email=session.get('signup_email'),
                password=session.get('signup_password')
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Signup successful! Please sign in.", "success")
            return redirect(url_for('signin'))
        else:
            flash("Invalid OTP. Please try again.", "error")
            return redirect(url_for('verify_signup_otp'))
    return render_template('verify_otp.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Duplicate email check
        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please sign in.", "error")
            return redirect(url_for('signup'))

        # Password match check
        if password != confirm_password:
            flash("Passwords do not match. Please try again.", "error")
            return redirect(url_for('signup'))

        # Password strength check
        import re
        pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,}$'
        if not re.match(pattern, password):
            flash("Password must be at least 6 characters, include a letter, a number, and a special character.", "error")
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        session['signup_password'] = hashed_password
        otp = str(random.randint(100000, 999999))
        session['signup_otp'] = otp
        session['signup_name'] = name
        session['signup_email'] = email

        msg = Message('Your OTP Code', sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f'Your OTP code is {otp}'
        try:
            mail.send(msg)
        except Exception as e:
            flash(f"Error sending OTP email: {e}", "error")
            return redirect(url_for('signup'))
        flash("OTP sent to your email. Please verify.", "success")
        return redirect(url_for('verify_signup_otp'))
    return render_template('signup.html', hide_signin_btn=True)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("No account found with this email.", "error")
            return redirect(url_for('forgot_password'))
        otp = str(random.randint(100000, 999999))
        session['reset_otp'] = otp
        session['reset_email'] = email
        msg = Message('Password Reset OTP', sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f'Your password reset OTP is {otp}'
        try:
            mail.send(msg)
        except Exception as e:
            flash(f"Error sending OTP email: {e}", "error")
            return redirect(url_for('forgot_password'))
        flash("OTP sent to your email. Please verify.", "success")
        return redirect(url_for('reset_password_otp'))
    return render_template('forgot_password.html', hide_signin_btn=True)

@app.route('/reset_password_otp', methods=['GET', 'POST'])
def reset_password_otp():
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        if user_otp == session.get('reset_otp'):
            return redirect(url_for('reset_password'))
        else:
            flash("Invalid OTP. Please try again.", "error")
            return redirect(url_for('reset_password_otp'))
    return render_template('reset_password_otp.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash("Passwords do not match. Please try again.", "error")
            return redirect(url_for('reset_password'))
        import re
        pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,}$'
        if not re.match(pattern, password):
            flash("Password must be at least 6 characters, include a letter, a number, and a special character.", "error")
            return redirect(url_for('reset_password'))
        hashed_password = generate_password_hash(password)
        user = User.query.filter_by(email=session.get('reset_email')).first()
        if user:
            user.password = hashed_password
            db.session.commit()
            session.pop('reset_email', None)
            session.pop('reset_otp', None)
            flash("Password reset successful! Please sign in.", "success")
            return redirect(url_for('signin'))
        else:
            flash("User not found.", "error")
            return redirect(url_for('reset_password'))
    return render_template('reset_password.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('signin'))

@app.route('/dashboard')
def dashboard():
    if 'name' in session:
        name = session['name']
        email = session['email']
        return render_template('dashboard.html', name=name, email=email,hide_signin_btn=True)
    else:
        return redirect(url_for('signin'))

@app.route('/admin')
def admin_panel():
    # Check if logged-in user is admin
    if 'email' not in session:
        return redirect(url_for('signin'))
    user = User.query.filter_by(email=session['email']).first()
    if not user or not user.is_admin:
        abort(403)  # Forbidden
    users = User.query.all()
    logs = UserLog.query.order_by(UserLog.timestamp.desc()).all()
    return render_template('admin_panel.html', users=users, logs=logs)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)