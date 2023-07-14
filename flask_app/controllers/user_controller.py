from flask import Flask, render_template, request, redirect, request, session, flash
from flask_app import app
from flask_app.models.user_model import User
from flask_app.models import ride_model
from flask_bcrypt import Bcrypt        
bcrypt = Bcrypt(app)

@app.route("/")
def login_page():
    return render_template("login.html")

@app.route('/register/user', methods=["POST"])
def register():
    raw_user_data = request.form
    if not User.new_email(raw_user_data):
        print("not new")
        flash("Already an email address. Please log in.")
        return redirect('/')
    if not User.validate(raw_user_data):
        return redirect('/')
    pw_hash = bcrypt.generate_password_hash(raw_user_data['password'])
    print(pw_hash)
    valid_user_data = {
        "first_name": raw_user_data["first_name"],
        "last_name": raw_user_data["last_name"],
        "password": pw_hash,
        "email": raw_user_data["email"]
    }
    new_user_id=User.save(valid_user_data) #database has now returned the id of the new created user
    session['first_name'] = valid_user_data['first_name'] #session is a dictionary of whatever data is currently accessible
    session['last_name'] = valid_user_data['last_name']
    session['email'] = valid_user_data['email']
    session['user_id'] = new_user_id
    return redirect('/dashboard')

@app.route("/reg_success")
def reg_success():
    return render_template("dashboard.html")

@app.route('/login/user', methods=["POST"])
def login_user():
    log_in_data = request.form
    print("THIS IS LOG_IN_DATA=", log_in_data)
    log_in_user = User.get_by_email(log_in_data["email"])
    if not log_in_user:
        flash('Please Register First', 'login')
        return redirect('/')
    if not User.validate_login(log_in_data["password"], log_in_user): 
        flash('Please Register First', 'login')
        return redirect('/')
    session['first_name'] = log_in_user.first_name #session is a dictionary of whatever data is currently accessible
    session['last_name'] = log_in_user.last_name
    session['email'] = log_in_user.email
    session['user_id'] = log_in_user.id
    print('LOGIN SUCCESS')
    return redirect('/dashboard')

@app.route("/login_success")
def login_success():
    if 'user_id' in session:
        return render_template("dashboard.html")
    else:
        redirect('/login')

@app.route("/logout")
def logout():
    session.clear()
    print("session cleared")
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if 'user_id' in session:
        current_user = User.get_by_id(session['user_id'])
    all_rides = ride_model.Ride.get_all()
    print("RIDES TO DASHBOARD:", all_rides)
    return render_template("dashboard.html", all_rides=all_rides, user=current_user)



