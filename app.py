# app.py
from flask import Flask, render_template, request, redirect, url_for, session,flash , abort
from datetime import timedelta , datetime
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random,os,json, uuid
from dotenv import load_dotenv
from analysis import plot_radar_chart, plot_study_hours, plot_subject_marks

# Initialize Flask app
app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=30)
load_dotenv()  # This loads variables from .env into environment
SECRET_KEY = os.getenv('SECRET_KEY')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

# SQLAlchemy config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'users.db')
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
    user = db.relationship('User', backref='logs') 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  

class StudentInput(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100))
    student_id = db.Column(db.String(50),unique=True)  # Unique student ID
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    location = db.Column(db.String(20))
    parent_edu = db.Column(db.String(50))
    education_level = db.Column(db.String(50))
    subjects = db.Column(db.Text)  # JSON string: {"Math": 95, ...}
    cpi_cgpa = db.Column(db.Float)
    class_rank = db.Column(db.Integer)
    backlogs = db.Column(db.Integer)
    attendance = db.Column(db.Float)
    leaves = db.Column(db.Integer)
    participation = db.Column(db.String(20))
    project_ontime = db.Column(db.String(10))
    study_hours = db.Column(db.Float)
    platforms = db.Column(db.Text)  # JSON string: ["YouTube", ...]
    study_style = db.Column(db.String(20))
    sports = db.Column(db.String(10))
    clubs = db.Column(db.String(100))
    volunteer = db.Column(db.String(10))
    sleep_hours = db.Column(db.Float)
    screen_time = db.Column(db.Float)
    stress = db.Column(db.String(20))
    career_interest = db.Column(db.String(100))
    higher_studies = db.Column(db.String(20))
    internship = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    favorite_feature = db.Column(db.String(50))
    ease_of_use = db.Column(db.String(50))
    feedback = db.Column(db.Text, nullable=False)
    rating = db.Column(db.String(10))
    recommend = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def parse_stress(stress_value):
    if isinstance(stress_value, (int, float)):
        return float(stress_value)
    if isinstance(stress_value, str):
        try:
            return float(stress_value)
        except ValueError:
            mapping = {'low': 3, 'medium': 6, 'high': 9}
            return mapping.get(stress_value.strip().lower(), 5)
    return 5

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
            user = User.query.filter_by(email=session.get('email')).first()
            if user:
                log = UserLog(user_id=user.id)
                db.session.add(log)
                db.session.commit()
            # Check if student info exists
            student_input = StudentInput.query.filter_by(email=session.get('email')).order_by(StudentInput.id.desc()).first()
            if student_input:
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Please complete your profile information.", "info")
                return redirect(url_for('update_info'))
        else:
            flash("Invalid OTP. Please try again.", "error")
            return redirect(url_for('verify_otp'))
    return render_template('verify_otp.html',hide_signin_btn=True)

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
    return render_template('verify_otp.html',hide_signin_btn=True)

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
    return render_template('reset_password_otp.html',hide_signin_btn=True)

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
    return render_template('reset_password.html',hide_signin_btn=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('signin'))

@app.route('/dashboard')
def dashboard():
    if 'name' in session:
        name = session['name']
        email = session['email']

        student = StudentInput.query.filter_by(email=email).order_by(StudentInput.id.desc()).first()

# <--Profile Summary -->
        profile_summary = None
        if student:
            profile_summary = {
                "name": student.name,
                "email": student.email,
                "student_id": student.student_id,
                "age": student.age,
                "gender": student.gender,
                "education_level": student.education_level,
                "cpi_cgpa": student.cpi_cgpa,
                "class_rank": student.class_rank,
            }

# <--Performance Summary -->
        performance_summary = None
        ai_summary = None

        if student:
            subjects = json.loads(student.subjects) if student.subjects else {}
            avg_marks = round(sum(map(float, subjects.values())) / len(subjects), 2) if subjects else 0
            backlogs = int(student.backlogs or 0)
            attendance = float(student.attendance or 0)
            study_hours = float(student.study_hours or 0)
            sleep_hours = float(student.sleep_hours or 0)
            screen_time = float(student.screen_time or 0)
            stress = parse_stress(student.stress)

            # Academic Health Score (overall)
            health_score = int((avg_marks * 0.4) + (attendance * 0.2) + (study_hours * 10 * 0.2) - (backlogs * 10))
            health_score = max(0, min(100, health_score))
            if health_score >= 80:
                health_label = "🌟 Excellent"
            elif health_score >= 60:
                health_label = "👍 Good"
            elif health_score >= 40:
                health_label = "⚠️ Average"
            else:
                health_label = "🔻 Weak"

            # Academic Section
            if avg_marks >= 80:
                academic_label = "Excellent"
            elif avg_marks >= 60:
                academic_label = "Good"
            elif avg_marks >= 40:
                academic_label = "Average"
            else:
                academic_label = "Needs Improvement"

            # Attendance Section
            if attendance >= 90:
                attendance_label = "Excellent"
            elif attendance >= 75:
                attendance_label = "Good"
            elif attendance >= 60:
                attendance_label = "Average"
            else:
                attendance_label = "Needs Improvement"

            # Study Habits Section
            if study_hours >= 6:
                study_label = "Healthy"
            elif study_hours >= 3:
                study_label = "Moderate"
            else:
                study_label = "Needs More Focus"

            # Lifestyle Section
            if sleep_hours >= 7 and stress <= 5 and screen_time <= 4:
                lifestyle_label = "Balanced"
            else:
                lifestyle_label = "Needs Attention"

            # Extracurricular Section
            def is_participating(val):
                return val and str(val).strip().lower() not in ['no', 'none', '']

            # Check if the student is participating in any extracurricular activities
            if (
            is_participating(student.clubs) or
            is_participating(student.volunteer) or
            is_participating(student.sports)
            ):
                extra_label = "Active"
            else:
                extra_label = "Consider Participating"

            performance_summary = {
                "health_score": health_score,
                "health_label": health_label,
                "academic_label": academic_label,
                "attendance_label": attendance_label,
                "study_label": study_label,
                "lifestyle_label": lifestyle_label,
                "extra_label": extra_label,
            }

            # --- AI Prediction Quick View ---
            predicted_score = (
                (avg_marks * 0.5) +
                (attendance or 0) * 0.2 +
                (study_hours or 0) * 5 -
                (backlogs or 0) * 5
            )
            predicted_score = max(0, min(100, predicted_score))
            confidence = 80  # Static for now

            ai_summary = {
                "predicted_score": round(predicted_score, 2),
                "confidence": confidence
            }

        return render_template(
            'dashboard.html',
            name=name,
            email=email,
            profile_summary=profile_summary,
            performance_summary=performance_summary,
            ai_summary=ai_summary,  
            hide_signin_btn=True
        )
    else:
        return redirect(url_for('signin'))

@app.route('/profile')
def profile():
    if 'email' not in session:
        return redirect(url_for('signin'))

    student_input = StudentInput.query.filter_by(email=session['email']).order_by(StudentInput.id.desc()).first()
    if not student_input:
        # If no info, redirect to update_info for first-time entry
        return redirect(url_for('update_info'))

    student = {
        "name": student_input.name,
        "email": student_input.email,
        "student_id": student_input.student_id,
        "age": student_input.age,
        "gender": student_input.gender,
        "location": student_input.location,
        "parent_edu": student_input.parent_edu,
        "education_level": student_input.education_level,
        "subjects": json.loads(student_input.subjects) if student_input.subjects else {},
        "cpi_cgpa": student_input.cpi_cgpa,
        "class_rank": student_input.class_rank,
        "backlogs": student_input.backlogs,
        "attendance": student_input.attendance,
        "leaves": student_input.leaves,
        "participation": student_input.participation,
        "project_ontime": student_input.project_ontime,
        "study_hours": student_input.study_hours,
        "platforms": json.loads(student_input.platforms) if student_input.platforms else [],
        "study_style": student_input.study_style,
        "sports": student_input.sports,
        "clubs": student_input.clubs,
        "volunteer": student_input.volunteer,
        "sleep_hours": student_input.sleep_hours,
        "screen_time": student_input.screen_time,
        "stress": student_input.stress,
        "career_interest": student_input.career_interest,
        "higher_studies": student_input.higher_studies,
        "internship": student_input.internship
    }
    return render_template('profile.html', student=student,hide_signin_btn=True)

@app.route('/update_info', methods=['GET', 'POST'])
def update_info():
    if 'email' not in session:
        return redirect(url_for('signin'))

    student_input = StudentInput.query.filter_by(email=session['email']).order_by(StudentInput.id.desc()).first()

    if request.method == 'POST':
        # --- REQUIRED FIELD VALIDATION START ---
        required_fields = [
            'name', 'age', 'gender', 'location', 'parent_edu', 'education_level',
            'class_rank', 'backlogs', 'attendance', 'leaves', 'participation',
            'project_ontime', 'study_hours', 'study_style', 'sleep_hours',
            'screen_time', 'stress', 'career_interest', 'higher_studies'
        ]
        for field in required_fields:
            value = request.form.get(field)
            if not value or value.strip() == "":
                flash(f"{field.replace('_', ' ').title()} is required.", "danger")
                return redirect(url_for('update_info'))

        # Special check for at least one subject
        subject_names = request.form.getlist('subject_names[]')
        subject_marks = request.form.getlist('subject_marks[]')
        if not subject_names or not subject_marks or len(subject_names) == 0:
            flash("At least one subject and mark is required.", "danger")
            return redirect(url_for('update_info'))
        # --- REQUIRED FIELD VALIDATION END ---

        # Now continue with your normal form data gathering and saving...
        subjects = {name: mark for name, mark in zip(subject_names, subject_marks)}
        platforms = request.form.getlist('platforms[]')

        # --- Checkbox handling START ---
        sports = request.form.get('sports', 'No')
        volunteer = request.form.get('volunteer', 'No')
        internship = request.form.get('internship', 'No')
        # --- Checkbox handling END ---

        if student_input:
             # Auto-generate student_id if missing
            if not student_input.student_id or student_input.student_id.strip() == "":
                student_input.student_id = str(uuid.uuid4())[:8]
           
            # Update existing record (keep the same student_id if already present)
            student_input.name = request.form.get('name')
            # student_input.student_id = student_input.student_id  # No change
            student_input.age = request.form.get('age')
            student_input.gender = request.form.get('gender')
            student_input.location = request.form.get('location')
            student_input.parent_edu = request.form.get('parent_edu')
            student_input.education_level = request.form.get('education_level')
            student_input.subjects = json.dumps(subjects)
            student_input.cpi_cgpa = request.form.get('cpi_cgpa') or None
            student_input.class_rank = request.form.get('class_rank')
            student_input.backlogs = request.form.get('backlogs')
            student_input.attendance = request.form.get('attendance')
            student_input.leaves = request.form.get('leaves')
            student_input.participation = request.form.get('participation')
            student_input.project_ontime = request.form.get('project_ontime')
            student_input.study_hours = request.form.get('study_hours')
            student_input.platforms = json.dumps(platforms)
            student_input.study_style = request.form.get('study_style')
            student_input.sports = sports
            student_input.clubs = request.form.get('clubs')
            student_input.volunteer = volunteer
            student_input.sleep_hours = request.form.get('sleep_hours')
            student_input.screen_time = request.form.get('screen_time')
            student_input.stress = request.form.get('stress')
            student_input.career_interest = request.form.get('career_interest')
            student_input.higher_studies = request.form.get('higher_studies')
            student_input.internship = internship
        else:
            # Create new record with auto-generated student_id
            student_input = StudentInput(
                email=session['email'],
                name=request.form.get('name'),
                student_id=str(uuid.uuid4())[:8],  # Auto-generate unique ID
                age=request.form.get('age'),
                gender=request.form.get('gender'),
                location=request.form.get('location'),
                parent_edu=request.form.get('parent_edu'),
                education_level=request.form.get('education_level'),
                subjects=json.dumps(subjects),
                cpi_cgpa=request.form.get('cpi_cgpa') or None,
                class_rank=request.form.get('class_rank'),
                backlogs=request.form.get('backlogs'),
                attendance=request.form.get('attendance'),
                leaves=request.form.get('leaves'),
                participation=request.form.get('participation'),
                project_ontime=request.form.get('project_ontime'),
                study_hours=request.form.get('study_hours'),
                platforms=json.dumps(platforms),
                study_style=request.form.get('study_style'),
                sports=request.form.get('sports'),
                clubs=request.form.get('clubs'),
                volunteer=request.form.get('volunteer'),
                sleep_hours=request.form.get('sleep_hours'),
                screen_time=request.form.get('screen_time'),
                stress=request.form.get('stress'),
                career_interest=request.form.get('career_interest'),
                higher_studies=request.form.get('higher_studies'),
                internship=request.form.get('internship')
            )
            db.session.add(student_input)
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))

    # On GET, pass existing data (if any) to pre-fill the form
    student = None
    if student_input:
        student = {
            "name": student_input.name,
            "student_id": student_input.student_id,
            "age": student_input.age,
            "gender": student_input.gender,
            "location": student_input.location,
            "parent_edu": student_input.parent_edu,
            "education_level": student_input.education_level,
            "subjects": json.loads(student_input.subjects) if student_input.subjects else {},
            "cpi_cgpa": student_input.cpi_cgpa,
            "class_rank": student_input.class_rank,
            "backlogs": student_input.backlogs,
            "attendance": student_input.attendance,
            "leaves": student_input.leaves,
            "participation": student_input.participation,
            "project_ontime": student_input.project_ontime,
            "study_hours": student_input.study_hours,
            "platforms": json.loads(student_input.platforms) if student_input.platforms else [],
            "study_style": student_input.study_style,
            "sports": student_input.sports,
            "clubs": student_input.clubs,
            "volunteer": student_input.volunteer,
            "sleep_hours": student_input.sleep_hours,
            "screen_time": student_input.screen_time,
            "stress": student_input.stress,
            "career_interest": student_input.career_interest,
            "higher_studies": student_input.higher_studies,
            "internship": student_input.internship
        }
    return render_template('update_info.html', student=student, hide_signin_btn=True)

@app.route('/performance_analysis')
def performance_analysis():
    if 'email' not in session:
        return redirect(url_for('signin'))

    student_input = StudentInput.query.filter_by(email=session['email']).order_by(StudentInput.id.desc()).first()
    if not student_input:
        flash("Please complete your profile information.", "info")
        return redirect(url_for('update_info'))

    subjects = json.loads(student_input.subjects) if student_input.subjects else {}
    platforms = json.loads(student_input.platforms) if student_input.platforms else []
    avg_marks = round(sum(map(float, subjects.values())) / len(subjects), 2) if subjects else 0
    backlogs = int(student_input.backlogs or 0)
    attendance = float(student_input.attendance or 0)
    study_hours = float(student_input.study_hours or 0)
    sleep_hours = float(student_input.sleep_hours or 0)
    screen_time = float(student_input.screen_time or 0)
    stress = parse_stress(student_input.stress)

    # Academic Health Score (overall)
    health_score = int((avg_marks * 0.4) + (attendance * 0.2) + (study_hours * 10 * 0.2) - (backlogs * 10))
    health_score = max(0, min(100, health_score))
    if health_score >= 80:
        health_label = "🌟 Excellent"
    elif health_score >= 60:
        health_label = "👍 Good"
    elif health_score >= 40:
        health_label = "⚠️ Average"
    else:
        health_label = "🔻 Weak"

    # --- Section Labels ---
    # Academic Section
    if avg_marks >= 80:
        academic_label = "Excellent"
    elif avg_marks >= 60:
        academic_label = "Good"
    elif avg_marks >= 40:
        academic_label = "Average"
    else:
        academic_label = "Needs Improvement"

    # Attendance Section
    if attendance >= 90:
        attendance_label = "Excellent"
    elif attendance >= 75:
        attendance_label = "Good"
    elif attendance >= 60:
        attendance_label = "Average"
    else:
        attendance_label = "Needs Improvement"

    # Study Habits Section
    if study_hours >= 6:
        study_label = "Healthy"
    elif study_hours >= 3:
        study_label = "Moderate"
    else:
        study_label = "Needs More Focus"

    # Lifestyle Section
    if sleep_hours >= 7 and stress <= 5 and screen_time <= 4:
        lifestyle_label = "Balanced"
    else:
        lifestyle_label = "Needs Attention"

    def is_participating(val):
        return val and str(val).strip().lower() not in ['no', 'none', '']

    # Extracurricular Section
    if (
    is_participating(student_input.clubs) or
    is_participating(student_input.volunteer) or
    is_participating(student_input.sports)
    ):
        extra_label = "Active"
    else:
        extra_label = "Consider Participating"

    # --- Plots ---
    plots_dir = os.path.join('static', 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    subject_marks_chart = plot_subject_marks(subjects, session['email'], plots_dir)
    study_hours_chart = plot_study_hours(study_hours, session['email'], plots_dir)
    radar_chart = plot_radar_chart(sleep_hours, screen_time, stress, study_hours, session['email'], plots_dir)

    return render_template(
        'performance_analysis.html',
        student=student_input,
        subjects=subjects,
        avg_marks=avg_marks,
        backlogs=backlogs,
        attendance=attendance,
        study_hours=study_hours,
        sleep_hours=sleep_hours,
        screen_time=screen_time,
        stress=stress,
        platforms=platforms,
        health_score=health_score,
        health_label=health_label,
        academic_label=academic_label,
        attendance_label=attendance_label,
        study_label=study_label,
        lifestyle_label=lifestyle_label,
        extra_label=extra_label,
        subject_marks_chart=subject_marks_chart,
        study_hours_chart=study_hours_chart,
        radar_chart=radar_chart,
        hide_signin_btn=True
    )

@app.route('/ai_prediction')
def ai_prediction():
    if 'email' not in session:
        return redirect(url_for('signin'))

    # Fetch student data from your database
    student = StudentInput.query.filter_by(email=session['email']).first()
    if not student:
        flash("No data found for this student.", "danger")
        return redirect(url_for('dashboard'))

    # Calculate average marks from the 'subjects' field (dummy logic)
    import json
    try:
        subjects_dict = json.loads(student.subjects.replace('""', '"').replace("'", '"'))
        avg_marks = sum(float(v) for v in subjects_dict.values()) / len(subjects_dict) if subjects_dict else 0
    except Exception:
        avg_marks = 0

    # Dummy prediction logic (simple formula)   , it will be replaced with a real ML model in future
    predicted_score = (
        (avg_marks * 0.5) +
        (student.attendance or 0) * 0.2 +
        (student.study_hours or 0) * 5 -
        (student.backlogs or 0) * 5
    )
    predicted_score = max(0, min(100, predicted_score))  # Clamp between 0 and 100
    confidence = 80  # Static value for now

    # Suggestions and action plan logic
    suggestions = []
    if (student.study_hours or 0) < 2:
        suggestions.append("Increase your daily study hours to at least 2.")
    if (student.sleep_hours or 0) < 7:
        suggestions.append("Ensure you get at least 7 hours of sleep daily.")
    if (student.screen_time or 0) > 4:
        suggestions.append("Reduce your screen time to less than 4 hours daily.")
    if (student.stress or '').lower() == 'high':
        suggestions.append("Manage your stress levels through relaxation techniques.")
    if student.education_level and student.education_level.lower() != 'school':
        if (student.cpi_cgpa or 0) < 6:
            suggestions.append("Focus on improving your CPI/CGPA to above 6.")
    if (student.attendance or 0) < 75:
        suggestions.append("Improve your attendance for better results.")
    if (student.backlogs or 0) > 0:
        suggestions.append("Focus on clearing your backlogs.")
    if (student.class_rank or 0) > 50:
        suggestions.append("Aim to improve your class rank by focusing on weak subjects.")
    if (str(student.project_ontime or '').strip().lower() in ['never','sometimes', 'rarely']):
        suggestions.append("Ensure you submit your projects on time to avoid penalties.")
    if not suggestions:
        suggestions.append("Keep up the good work!")

    action_plan = [
        "Revise weak subjects regularly.",
        "Maintain consistent study hours.",
        "Seek help from teachers if needed."
    ]

    motivational_quote = "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle."
    risk_alert = None
    if predicted_score < 70:
        risk_alert = "Your predicted score is below 70. Please focus on your studies and seek help if needed."
    print("Predicted Score:", predicted_score, "Confidence:", confidence)
    return render_template(
        'ai_prediction.html',
        predicted_score=round(predicted_score, 2),
        confidence=confidence,
        motivational_quote=motivational_quote,
        suggestions=suggestions,
        action_plan=action_plan,
        risk_alert=risk_alert,
        hide_signin_btn=True
    )

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        favorite_feature = request.form.get('favorite_feature')
        ease_of_use = request.form.get('ease_of_use')
        feedback_text = request.form.get('feedback')
        rating = request.form.get('rating')
        recommend = request.form.get('recommend')

        fb = Feedback(
            name=name,
            email=email,
            favorite_feature=favorite_feature,
            ease_of_use=ease_of_use,
            feedback=feedback_text,
            rating=rating,
            recommend=recommend
        )
        db.session.add(fb)
        db.session.commit()
        flash("Thank you for your feedback!", "success")
        return redirect(url_for('dashboard'))

    return render_template('feedback.html',hide_signin_btn=True)

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
    return render_template('admin_panel.html', users=users, logs=logs,hide_signin_btn=True)

@app.route('/admin/feedback')
def admin_feedback():
    feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).all()
    return render_template('admin_feedback.html', feedbacks=feedbacks,hide_signin_btn=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)

# Deployment Note ---->>>
    ### Note: Deployment will require some charges like Heroku, AWS, etc. ### , It will be deployed on proffesor"s Advice later
    # For now, it is running locally for testing and development purposes.