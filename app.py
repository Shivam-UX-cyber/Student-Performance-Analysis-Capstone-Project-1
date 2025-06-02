# app.py
# A simple Flask application with multiple routes and templates
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a strong secret key
app.permanent_session_lifetime = timedelta(minutes=30)




# Routes

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        session.permanent = True
        name = request.form.get('name')
        email = request.form.get('email')

        # Save user details in session
        session['name'] = name
        session['email'] = email

        return redirect(url_for('dashboard'))
    return render_template('signin.html')

@app.route('/dashboard')
def dashboard():
    if 'name' in session:
        name = session['name']
        email = session['email']
        return render_template('dashboard.html', name=name, email=email)
    else:
        return redirect(url_for('signin'))
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('signin'))




@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/learn_more')
def learn_more():
    return render_template('learn_more.html')

if __name__ == '__main__':
    app.run(debug=True)