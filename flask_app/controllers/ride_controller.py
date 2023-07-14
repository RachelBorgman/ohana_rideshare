from flask import Flask, render_template, request, redirect, request, session, flash
from flask_app import app
from flask_app.models import ride_model
from flask_app.controllers import user_controller
from flask_app.models import user_model
from flask_bcrypt import Bcrypt   
import pprint     
bcrypt = Bcrypt(app)

@app.route("/request_ride")
def request_ride():
    print('RENDERING REQUEST_RIDE TEMPLATE')
    return render_template("request_ride.html")

@app.route('/request', methods=['POST'])
def request_new_ride():
    raw_ride_data = request.form
    print("this is the raw_ride_data:", raw_ride_data)
    if not 'user_id' in session:
        flash('please log in', 'ride')
        return redirect('/request_ride')
    if not ride_model.Ride.validate_ride(raw_ride_data):
        return redirect('/request_ride')
    print("Validating Ride!!")
    # else no errors:
    valid_ride_data = {
        "destination": raw_ride_data["destination"],
        "details": raw_ride_data["details"],
        "pick_up_loc": raw_ride_data["pick_up_loc"],
        "ride_date": raw_ride_data["ride_date"],
        "rider": raw_ride_data["rider"]
    }
    print("This is the valid_ride_data:", valid_ride_data)
    new_ride_id = ride_model.Ride.save(valid_ride_data)
    print('This is the new ride id=', new_ride_id)
    return redirect("/dashboard")

@app.route('/ride_details/<int:ride_id>')
def ride_details(ride_id):
    ride_data = {
        "id":ride_id
    }
    ride_to_view = ride_model.Ride.get_one(ride_data)
    print("the ride:")
    print(ride_to_view)
    driver = ride_model.Ride.get_driver_by_id(ride_data)
    return render_template("ride_details.html", ride=ride_to_view, driver=driver)

@app.route('/update_ride/<int:ride_id>')
def update(ride_id):
    ride_data = {
        "id":ride_id
    }
    ride = ride_model.Ride.get_by_id(ride_data)
    return render_template('update_ride.html', ride=ride)

@app.route('/update_ride/<int:ride_id>', methods=['POST'])
def update_ride(ride_id):
    raw_ride_data = request.form
    if not ride_model.Ride.validate_ride_update(raw_ride_data):
        return redirect(f"/update_recipe/{ride_id}")
    valid_ride_data = {
        'id': ride_id,
        "details": raw_ride_data["details"],
        "pick_up_loc": raw_ride_data["pick_up_loc"],
        "rider": raw_ride_data["rider"]
    }
    ride_model.Ride.update(valid_ride_data)
    return redirect('/dashboard')

@app.route("/request_to_drive/<int:ride_id>", methods=["POST"])
def request_to_drive(ride_id):
    raw_ride_data = request.form
    ride_data = {
        "id":ride_id,
        "driver": raw_ride_data["driver"]
    }
    ride_model.Ride.assign_driver(ride_data)
    print("this is the driver:")
    # driver_info = ride_model.Ride.get_driver_by_id(ride_data)
    # driver = driver_info['first_name']
    # print("this is the driver:", driver)
    return redirect("/dashboard", )

@app.route('/cancel_drive/<int:ride_id>')
def cancel_drive(ride_id):
    ride_data = {
        "id":ride_id
    }
    ride_model.Ride.cancel_drive(ride_data)
    return redirect('/dashboard')

@app.route('/delete/<int:ride_id>')
def delete(ride_id):
    ride_model.Ride.delete(ride_id)
    return redirect('/dashboard')