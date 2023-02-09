from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm, EditFeedbackForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Halo03117!@localhost:5432/feedback_db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.app_context().push()


connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    return redirect('/register')

@app.route('/register', methods = ["GET", "POST"])
def register_user():
    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        db.session.commit()

        session['user_username'] = new_user.username
        flash("Registration succesful, you are now logged in!", "success")
        return redirect(f'/users/{new_user.username}')
    else:
        return render_template('register.html', form = form)

@app.route('/login', methods=["GET", "POST"])
def login_user():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username,password)

        if user:
            flash(f"Welcome Back {user.username}!", "success")
            session['user_username'] = user.username
            return redirect(f'/users/{user.username}')
        else: 
            form.username.errors = ['Invalid username/password']
    return render_template('login.html', form = form)

@app.route('/logout')
def logout_user():
    session.pop('user_username')
    flash('Log out successful', 'success')
    return redirect('/')

@app.route('/users/<username>')
def display_user(username):
    user = User.query.get(username)
    
    if 'user_username' not in session:
        flash("Please register or log in!", "danger")
        return redirect('/')
    else:
        return render_template('users.html', user = user)

@app.route('/users/<username>/delete', methods = ["POST"])
def delete_user(username):
    user = User.query.get_or_404(username)

    if 'user_username' not in session:
        flash('Please log in first')
        return redirect('/login')
    else:
        session.pop('user_username')
        db.session.delete(user)
        db.session.commit()
        flash('Account deleted', 'danger')
        return redirect('/')

@app.route('/users/<username>/feedback/add', methods = ["GET", "POST"])
def add_feedback(username):
    
    if 'user_username' not in session:
        flash('Please log in first')
        return redirect('/login')
    else:
        form = FeedbackForm()
        user = User.query.get_or_404(username)

        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data

            new_feedback = Feedback(title = title, content = content, username = user.username)
            db.session.add(new_feedback)
            db.session.commit()
            flash('Feedback added', 'success')
            return redirect(f'/users/{username}') 
        else:
            return render_template('feedback.html', form = form)

@app.route('/feedback/<int:feedback_id>/update', methods = ["GET", "POST"])
def update_feedback(feedback_id):
    if 'user_username' not in session:
        flash('Please log in first')
        return redirect('/login')
    else: 
        feedback = Feedback.query.get(feedback_id)
        form = EditFeedbackForm(title = feedback.title, content = feedback.content)

        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data

            feedback.title = title
            feedback.content = content
            db.session.commit()
            flash("Saved changes", "success")
            return redirect(f'/users/{feedback.username}')
        return render_template('edit_feedback.html', form = form)

@app.route('/feedback/<int:feedback_id>/delete', methods = ["POST"])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    flash("Feedback deleted", "success")
    return redirect(f'/users/{feedback.username}')


