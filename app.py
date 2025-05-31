from flask import Flask, render_template

app = Flask(__name__)

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

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/learn_more')
def learn_more():
    return render_template('learn_more.html')

if __name__ == '__main__':
    app.run(debug=True)