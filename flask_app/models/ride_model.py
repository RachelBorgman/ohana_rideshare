from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app import app
from flask_bcrypt import Bcrypt
from flask_app.models import user_model
from flask_app.controllers import ride_controller 
import re
import pprint

db = 'ohana'

class Ride: #class - predefined structure of data
    def __init__( self , ride_data: dict | None ): #can only pass a dictionary in to create User class
        self.id = ride_data['id'] #left is class attribute name, right side is database column names
        self.destination = ride_data['destination']
        self.pick_up_loc = ride_data['pick_up_loc']
        self.ride_date = ride_data['ride_date']
        self.details = ride_data['details']
        self.rider = ride_data['rider']
        self.driver = ride_data['driver']
        self.created_at = ride_data['created_at']
        self.updated_at = ride_data['updated_at']
        self.messages = None

    @staticmethod
    def validate_ride(raw_ride_data: dict):
        is_valid = True
        if len(raw_ride_data['destination']) < 3:
            flash("Destination must be at least 3 characters.", 'ride')
            is_valid = False
        if len(raw_ride_data['pick_up_loc']) < 3:
            flash("Pick-up Location must be at least 3 characters.", 'ride')
            is_valid = False
        if len(raw_ride_data['details']) < 10:
            flash("Instructions must be at least 3 characters.", 'ride')
            is_valid = False
        if raw_ride_data['ride_date'] is None:
            flash("Ride Date is a required field", 'ride')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_ride_update(raw_ride_data: dict):
        is_valid = True
        if len(raw_ride_data['pick_up_loc']) < 3:
            flash("Pick-up Location must be at least 3 characters.", 'ride')
            is_valid = False
        if len(raw_ride_data['details']) < 10:
            flash("Details must be at least 3 characters.", 'ride')
            is_valid = False
        return is_valid
    
    @classmethod
    def get_by_id(cls, ride_data):
        query = """
        SELECT * FROM ride
        WHERE id = %(id)s;
        """
        results = connectToMySQL(db).query_db(query, ride_data)
        if results:
            ride = results[0]
            return ride
        return False
    
    @classmethod
    def save(cls,data: dict): #data is dictionary being passed in from controller when it's called
        query = """INSERT INTO ride (destination, pick_up_loc, ride_date, details, rider) 
        VALUES (%(destination)s, %(pick_up_loc)s, %(ride_date)s, %(details)s, %(rider)s);
        """ #%() matches key from created dictionary being passed in
        return connectToMySQL(db).query_db(query, data)

    @classmethod
    def get_one(cls, ride_data):
        query = """
        SELECT ride.id, ride.destination, ride.pick_up_loc, ride.ride_date, ride.details, ride.rider, ride.driver, ride.created_at, ride.updated_at, user.id, user.first_name, user.last_name, user.email, user.created_at, user.updated_at
        FROM ride
        JOIN user ON ride.rider = user.id
        WHERE ride.id = %(id)s;
        """
        results = connectToMySQL(db).query_db(query, ride_data)
        if not results:
            return False
        for row in results:
            rider = user_model.User({
                "id": row["id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "email": row["email"],
                "created_at": row["user.created_at"],
                "updated_at": row["user.updated_at"],
                "password": ""
            })
            ride = Ride({
                "id": row["id"],
                "destination": row['destination'],
                'pick_up_loc': row['pick_up_loc'],
                'ride_date': row['ride_date'],
                'details': row['details'],
                'driver': row["driver"],
                'rider': rider,
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
            results = results[0]
        print('these are the get_one results:', results)
        return ride

    @classmethod
    def get_all(cls):
        query = """
        SELECT ride.id, ride.destination, ride.pick_up_loc, ride.ride_date, ride.details, ride.rider, ride.driver, ride.created_at, ride.updated_at, rider.id, rider.first_name, rider.last_name, rider.email, rider.created_at, rider.updated_at, driver.id, driver.first_name, driver.last_name, driver.email, driver.created_at, driver.updated_at
        FROM ride
        JOIN user AS rider ON ride.rider = rider.id
        LEFT JOIN user AS driver ON ride.driver = driver.id;
        """
        results = connectToMySQL(db).query_db(query)
        print("This is the get_all query results=", results)
        all_rides = []
        # print(results[0]['description'])
        for row in results:
            # rider = user_model.User.get_by_id(row['rider'])
            rider = user_model.User({
                "id": row["rider.id"], #Lets start talking here  it was "id"
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "email": row["email"],
                "created_at": row["rider.created_at"],
                "updated_at": row["rider.updated_at"],
                "password": ""
            })
            driver = None
            if row['driver'] is not None:
                # driver = user_model.User.get_by_id(row['driver'])
                driver = user_model.User({
                    "id": row["driver.id"],
                    "first_name": row["driver.first_name"],
                    "last_name": row["driver.last_name"],
                    "email": row["driver.email"],
                    "created_at": row["driver.created_at"],
                    "updated_at": row["driver.updated_at"],
                    "password": ""
                })
                
            ride = Ride({
                    "id": row["id"],
                    "destination": row['destination'],
                    'pick_up_loc': row['pick_up_loc'],
                    'ride_date': row['ride_date'],
                    'driver': driver,
                    'details': row['details'],
                    'rider': rider,
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            all_rides.append(ride)
        print("THESE ARE ALL_RIDES:", all_rides)
        return all_rides

    @classmethod
    def update(cls,valid_ride_data):
        query = """
            UPDATE ride
            SET pick_up_loc = %(pick_up_loc)s, details = %(details)s
            WHERE id = %(id)s;
        """
        results = connectToMySQL(db).query_db(query, valid_ride_data)
        return results

    @classmethod
    def delete(cls, ride_id: int):
        query = "DELETE FROM ride WHERE id = %(id)s;"
        results = connectToMySQL(db).query_db(query, {"id":ride_id})
        return results
    
    @classmethod
    def assign_driver(cls, ride_id: int):
        query = """
            UPDATE ride
            SET driver = %(driver)s
            WHERE id = %(id)s;
        """
        results = connectToMySQL(db).query_db(query, ride_id)
        return results
    
    @classmethod
    def cancel_drive(cls, ride_id: int):
        query = """
            UPDATE ride
            SET ride.driver = NULL
            WHERE id = %(id)s;
        """
        results = connectToMySQL(db).query_db(query, ride_id)
        return results
    
    @classmethod
    def get_driver_by_id(cls, ride_data):
        query = """
        SELECT user.first_name FROM user
        JOIN ride ON user.id = ride.driver
        WHERE ride.id = %(id)s;
        """
        results = connectToMySQL(db).query_db(query, ride_data)
        if results:
            driver = results[0]
            print("This is the driver:", driver)
            return driver
        return False