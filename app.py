from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret123"

# DB config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///decisions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# User table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))


# Decision table
class Decision(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    salary = db.Column(db.Integer)
    risk = db.Column(db.String(50))
    location = db.Column(db.String(50))
    result = db.Column(db.String(100))
    risk_level = db.Column(db.String(50))


# LOGIN PAGE
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        check = User.query.filter_by(username=user, password=pwd).first()

        if check:
            session['user'] = user
            return redirect('/home')
        else:
            return "Invalid Login ❌"

    return render_template('login.html')


# HOME PAGE
@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        salary = int(request.form['salary'])
        risk = request.form['risk']
        location = request.form['location']

        score = 0
        risk_score = 0

        if salary > 70000:
            score += 2
        elif salary > 40000:
            score += 1
        else:
            risk_score += 2

        if risk == 'low':
            score += 2
        elif risk == 'medium':
            score += 1
        else:
            risk_score += 2

        if location in ['city', 'metro']:
            score += 1
        else:
            risk_score += 1

        final_score = score - risk_score

        if final_score >= 3:
            decision_result = "Strong Yes ✅"
            risk_level = "Low"
        elif final_score >= 1:
            decision_result = "Consider 🤔"
            risk_level = "Medium"
        else:
            decision_result = "High Risk ❌"
            risk_level = "High"

        # Save
        new = Decision(
            salary=salary,
            risk=risk,
            location=location,
            result=decision_result,
            risk_level=risk_level
        )
        db.session.add(new)
        db.session.commit()

        return render_template('result.html', result=decision_result, risk=risk_level)

    return render_template('home.html')


# LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Create default user
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin', password='1234')
            db.session.add(user)
            db.session.commit()

    app.run(debug=True)