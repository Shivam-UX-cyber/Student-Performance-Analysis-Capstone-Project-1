# Student Performance Analysis Portal

A flask based web application for students and educators to analyze academic performance, get AI-driven insights, and manage accounts securely.

---

## 🚀 Features

- **User Authentication:** Sign up, sign in (with OTP), password reset, and secure session management.
- **Student Info Form:** Collects demographics, academics, attendance, study habits, extracurriculars, psychological factors, and future aspirations.
- **Personal Dashboard:** View your academic profile and access analysis tools.
- **Performance Analytics:** Visualize grades and trends.
- **AI Prediction:** Get smart predictions for future performance.
- **Support System:** Contact support via a built-in form (sends email to admin).
- **Admin Panel:** Manage users and view login logs (admin only).
- **Dynamic Subjects & Marks:** Add/remove subjects and auto-calculate average marks.
- **CPI/CGPA Field:** Shown only for college-level students.
- **Admin Panel:** View all students and submitted feedback.
- **Feedback System:** Users can submit feedback; admin can view all feedback.
- **Mobile Responsive:** Clean UI for desktop and mobile.
- **Data Visualization:** (If implemented) Performance analysis and AI prediction modules.
- **Security:** Passwords are hashed; session-based access control.


---

## 🛠️ Setup Instructions

### 1. Clone the repository

```sh
git clone https://github.com/Shivam-UX-cyber/Student-Performance-Analysis-Capstone-Project-1
cd student-performance-analysis
```

### 2. Create and activate a virtual environment

```sh
python -m venv env
env\Scripts\activate   # On Windows
# source env/bin/activate   # On Mac/Linux
```

### 3. Install dependencies

```sh
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file or set these in your environment:

```
SECRET_KEY=your_secret_key
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

Or edit `app.py` to set your email and secret key.

### 5. Initialize the database

```sh
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

### 6. Run the app

```sh
python app.py
```

Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 📄 Main Pages

- `/` — Home
- `/about` — About the project
- `/docs` — Documentation & FAQ
- `/support` — Contact support (sends email)
- `/learn_more` — Learn more about features & AI
- `/signup` — Create account
- `/signin` — Sign in (with OTP)
- `/dashboard` — User dashboard
- `/admin` — Admin panel (admin only)

---

## ✉️ Support

For help, use the [Support page](http://127.0.0.1:5000/support) or email: `support@example.com`

---
## 📝 Usage

- **Sign Up / Sign In:** Create an account or log in.
- **Update Info:** Fill out the student input form with all required details.
- **Dashboard:** Access your profile, performance analysis, update info, AI prediction, and feedback.
- **Admin Panel:** (If admin) View all students and feedback.
- **Feedback:** Submit feedback via the feedback form; admins can view all feedback.

---

## 📱 Mobile Responsiveness

- The UI is optimized for both desktop and mobile devices.
- Tables and forms are readable and usable on small screens.

---

## ⚠️ Security Notes

- Never commit your real email password or secret key to public repositories.
- Use environment variables or a `.env` file for sensitive info.
- For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) if 2FA is enabled.
- Passwords are securely hashed.
- Session management is used for authentication.
- Admin routes are protected.

---

## 🙏 Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [Jinja2](https://jinja.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Bootstrap](https://getbootstrap.com/) (if used)
- All open-source contributors and resources used.

---



## 📚 License

MIT License (add your license file if needed).

---

## 👨‍💻 Authors

- [Shivam_642 Shivam_637 Shivam_644 Shiv_631]
- IITP 2025 Capstone Project Team

---

**Happy Learning!**
