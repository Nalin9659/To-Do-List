from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Task, db
import os
from dotenv import load_dotenv

load_dotenv()


app =Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("SERET_KEY")
db.init_app(app) # Intialise the datebase with the flask app

# Step1: set up the login manager
login_manager= LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Step2: Login and Registration routes.

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('tasks'))
        else:
            flash("Invalid username or password")
    return render_template('login.html')

# Step3:Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form ['username']
        password = request.form ['password']
        hashed_password = generate_password_hash(password, method= 'pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! you can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Step4: Task Management CRUD Opertions.

@app.route('/dashbord', methods= ['GET', 'POST'])
@login_required
def tasks():
    if request.method == 'POST':
       task_content = request.form['content']
       new_task = Task(content=task_content, user_id=current_user.id)
       db.session.add(new_task)
       db.session.commit()
       return redirect(url_for('tasks'))
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('dashbord.html', tasks=tasks)

@app.route('/delete_task/<int:id>')
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id == current_user.id:
       db.session.delete(task)
       db.session.commit()
    return redirect(url_for('dashbord'))


@app.route('/complete/<int:id>')
@login_required
def complete(id):
    task = Task.query.get_or_404(id)
    if task.user_id == current_user.id:
       task.complete= True
       db.session.commit()
    return redirect(url_for('dashbord'))

# Step5: Create route for homepage
@app.route('/')
def home():
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)



