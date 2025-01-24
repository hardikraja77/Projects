from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session, send_file
import pyodbc
import os
import io
from datetime import datetime
import geopy.distance
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = '123'


# Database connection function (can be used for raw connections)
def get_db_connection():
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                              'SERVER=RAMESH\\SQLEXPRESS;'
                              'DATABASE=sales3;'
                              'Trusted_Connection=yes;')
        return conn
    except pyodbc.Error as e:
        print("Error connecting to database: ", e)
        return None
engine = create_engine('mssql+pyodbc://RAMESH\\SQLEXPRESS/sales3?driver=ODBC+Driver+17+for+SQL+Server')
# Authentication function with role checking
def authenticate_user(username, password):
    conn = get_db_connection()
    if conn is None:
        return None, None

    try:
        cursor = conn.cursor()
        query = "SELECT UserId, AccessType FROM Users WHERE Username = ? AND Password = ?"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        return (result[0], result[1]) if result else (None, None)
    except pyodbc.Error as e:
        print("Error during authentication: ", e)
        return None, None
    finally:
        conn.close()

# Index route
@app.route('/')
def index():
    return render_template('login.html')

# Login route
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    # Authenticate the user
    user_id, access_type = authenticate_user(username, password)

    if user_id:
        # Store user_id in session
        session['user_id'] = user_id

        # Insert location data and login time into the database
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                query = """INSERT INTO UserLocations (UserId, Latitude, Longitude, LoginTime)
                           VALUES (?, ?, ?, ?)"""
                login_time = datetime.now()
                cursor.execute(query, (user_id, latitude, longitude, login_time))
                conn.commit()
            except pyodbc.Error as e:
                print("Error inserting location data: ", e)
            finally:
                conn.close()

        # Redirect based on access type
        if access_type == 'Admin':
            return redirect(url_for('admin_dashboard'))
        elif access_type == 'Sales':
            return redirect(url_for('sales_dashboard'))
        elif access_type == 'Employee':
            return redirect(url_for('employee_dashboard'))
    else:
        flash('Login failed. Please check your username and password.')
        return redirect(url_for('index'))

# Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# Sales Dashboard
@app.route('/sales_dashboard')
def sales_dashboard():
    return render_template('sales_dashboard.html')

# Assuming a function to get the currently logged-in user ID
def get_logged_in_user_id():
    # Implement this function to get the currently logged-in user ID
    return 1  # Placeholder

class User:
    def __init__(self, username, password, access_type):
        self.username = username
        self.password = password
        self.access_type = access_type

# Route to display the Add New User form
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        # Get the data from the form
        username = request.form['username']
        password = request.form['password']
        access_type = request.form['access_type']

        # Create a new user instance
        new_user = User(username=username, password=password, access_type=access_type)

        # Add the new user to the database
        conn = get_db_connection()
        if conn is None:
            return "Database connection failed."

        try:
            cursor = conn.cursor()
            query = "INSERT INTO Users (Username, Password, AccessType) VALUES (?, ?, ?)"
            cursor.execute(query, (new_user.username, new_user.password, new_user.access_type))
            conn.commit()
            return redirect(url_for('success'))  # Redirect to the success page
        except Exception as e:
            conn.rollback()  # Roll back the transaction on error
            return f"An error occurred: {e}"
        finally:
            conn.close()  # Close the database connection

    return render_template('add_user.html')  # Render the form for GET requests

# Route to handle successful addition of user
@app.route('/success')
def success():
    return "User added successfully!"

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        task_id = request.form.get('taskId')
        email = request.form.get('email')
        requirements = request.form.get('requirements')
        photo = request.files.get('photos')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        # Validate task_id
        if not task_id or not task_id.isdigit():
            return "Invalid task ID.", 400

        # Convert task_id to integer
        task_id = int(task_id)

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()

                # Get customer details from the Tasks table
                cursor.execute("SELECT CustomerName, PhoneNumber, AssignedSalespersonId FROM Tasks WHERE TaskId = ?", (task_id,))
                task = cursor.fetchone()

                if task:
                    customer_name, contact_number, salesperson_id = task
                    logged_in_user_id = session.get('user_id')

                    if logged_in_user_id != salesperson_id:
                        # Redirect to request a new salesperson if the logged-in user is not the assigned salesperson
                        return render_template('request_salesperson.html', task_id=task_id)

                    # Read the photo binary data if provided
                    photo_binary = photo.read() if photo else None

                    # Insert customer details into CustomerDetails table
                    cursor.execute("""
                        INSERT INTO CustomerDetails (CustomerName, ContactNumber, Email, Requirements, Photo, Latitude, Longitude, SalespersonID)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (customer_name, contact_number, email, requirements, photo_binary, latitude, longitude, salesperson_id))

                    # Remove the task from the Tasks table
                    cursor.execute("DELETE FROM Tasks WHERE TaskId = ?", (task_id,))

                    conn.commit()
                    return "Customer added successfully!"

                else:
                    return "Task not found.", 404

            except pyodbc.Error as e:
                print(f"Error: {e}")
                conn.rollback()
                return "An error occurred while adding the customer.", 500

            finally:
                cursor.close()
                conn.close()
        else:
            return "Database connection failed.", 500

    elif request.method == 'GET':
        # Render the form page for GET requests
        return render_template('add_customer.html')

    return "Method Not Allowed", 405


@app.route('/request_salesperson', methods=['GET', 'POST'])
def request_salesperson():
    if request.method == 'POST':
        task_id = request.form.get('taskId')
        new_salesperson_id = request.form.get('newSalespersonId')

        if not task_id or not new_salesperson_id:
            return "Invalid request.", 400

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()

                # Update the task with the new salesperson
                cursor.execute("UPDATE Tasks SET AssignedSalespersonId = ? WHERE TaskId = ?", (new_salesperson_id, task_id))

                conn.commit()
                return "Task reassigned successfully! Please have the new salesperson accept the request."
            
            except pyodbc.Error as e:
                print(f"Error: {e}")
                conn.rollback()
                return "An error occurred while reassigning the task.", 500
            
            finally:
                cursor.close()
                conn.close()

        return "Database connection failed.", 500

    # GET request logic
    task_id = request.args.get('taskId')
    if task_id:
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()

                # Fetch the task details
                cursor.execute("SELECT TaskId, AssignedSalespersonId FROM Tasks WHERE TaskId = ?", task_id)
                task = cursor.fetchone()

                if task:
                    task_id, assigned_salesperson_id = task
                    return render_template('request_salesperson.html', task_id=task_id, assigned_salesperson_id=assigned_salesperson_id)
                else:
                    return "Task not found.", 404

            except pyodbc.Error as e:
                print(f"Error: {e}")
                return "An error occurred while fetching the task details.", 500

            finally:
                cursor.close()
                conn.close()

        return "Database connection failed.", 500
    
    return "Task ID not provided.", 400

# Route to retrieve customer information
@app.route('/view_customer', methods=['GET', 'POST'])
def view_customer():
    customer_data = None
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query = """SELECT CustomerID, CustomerName, ContactNumber, Email, Requirements, 
                              Photo, Latitude, Longitude, SalespersonID 
                       FROM CustomerDetails WHERE CustomerID = ?"""
            cursor.execute(query, (customer_id,))
            result = cursor.fetchone()

            if result:
                customer_data = {
                    'CustomerID': result[0],
                    'CustomerName': result[1],
                    'ContactNumber': result[2],
                    'Email': result[3],
                    'Requirements': result[4],
                    'Photo': result[5],  # Binary data for the image
                    'Latitude': result[6],
                    'Longitude': result[7],
                    'SalespersonID': result[8],
                }
        except pyodbc.Error as e:
            print("Error retrieving customer data: ", e)
            flash('Failed to retrieve customer data.')
        finally:
            conn.close()
    return render_template('view_customer.html', customer_data=customer_data)


@app.route('/fetch_all_customers', methods=['GET'])
def fetch_all_customers():
    all_customers = get_all_customers_from_db()  # Function to fetch all customer details
    return render_template('view_customer.html', all_customers=all_customers)


def get_all_customers_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT CustomerID, CustomerName FROM CustomerDetails")
    customers = cursor.fetchall()
    conn.close()
    return customers

# Route to serve the photo directly from the database
@app.route('/photo/<int:customer_id>')
def photo(customer_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT Photo FROM CustomerDetails WHERE CustomerID = ?"
        cursor.execute(query, (customer_id,))
        result = cursor.fetchone()

        if result:
            photo_binary = result[0]
            return send_file(io.BytesIO(photo_binary), mimetype='image/jpeg')
        else:
            return "Photo not found", 404
    except pyodbc.Error as e:
        print("Error retrieving photo: ", e)
        return "Error retrieving photo", 500
    finally:
        conn.close()

        
@app.route('/salesperson_location', methods=['GET'])
def salesperson_location():
    salesperson_id = request.args.get('salesperson_id')
    date = request.args.get('date')

    if not salesperson_id or not date:
        return jsonify({'error': 'Salesperson ID and Date are required'}), 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                    SELECT Latitude, Longitude, CreatedAt 
                    FROM CustomerDetails 
                    WHERE SalespersonId = ? AND CONVERT(date, CreatedAt) = ?
                    ORDER BY CreatedAt ASC
                    """
            cursor.execute(query, (salesperson_id, date))
            result = cursor.fetchall()

            if result:
                locations = [{'latitude': row[0], 'longitude': row[1], 'timestamp': row[2].strftime('%Y-%m-%d %H:%M:%S')} for row in result]
                return jsonify(locations)
            else:
                return jsonify([]), 200
        except pyodbc.Error as e:
            print("Error retrieving location data: ", e)
            return jsonify({'error': 'Failed to retrieve location data'}), 500
        finally:
            conn.close()
    return jsonify({'error': 'Database connection failed'}), 500



@app.route('/view_salesperson_map')
def view_salesperson_map():
    return render_template('view_salesperson_map.html')

# Route to monitor salesperson location
@app.route('/monitor_salesperson', methods=['GET'])
def monitor_salesperson():
    return render_template('monitor_salesperson.html')

@app.route('/customer_form', methods=['GET', 'POST'])
def customer_form():
    if request.method == 'POST':
        customer_name = request.form.get('customerName')
        phone_number = request.form.get('phoneNumber')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        # Insert the customer task into the Tasks table and assign it to the nearest salesperson
        success = assign_task_to_salesperson(customer_name, phone_number, latitude, longitude)

        if success:
            flash('Task created successfully and assigned to the nearest salesperson!')
            return 'Task created successfully!'  # Or use JSON response
        else:
            return 'Error creating task.', 500  # Return an appropriate error message

    return render_template('customer_form.html')

def assign_task_to_salesperson(customer_name, phone_number, latitude, longitude):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Fetch all active salespersons and their locations
            cursor.execute("""
                SELECT U.UserId, UL.Latitude, UL.Longitude 
                FROM Users U 
                JOIN UserLocations UL ON U.UserId = UL.UserId 
                WHERE U.AccessType = 'Sales' 
                AND UL.LoginTime = (
                    SELECT MAX(LoginTime) 
                    FROM UserLocations 
                    WHERE UserId = U.UserId
                )
            """)
            salespersons = cursor.fetchall()

            if not salespersons:
                print("No available salespersons found.")
                return False

            # Calculate the nearest salesperson
            salesperson_distances = []
            for sp in salespersons:
                sp_id, sp_lat, sp_lon = sp
                distance = geopy.distance.distance((latitude, longitude), (sp_lat, sp_lon)).km
                salesperson_distances.append((sp_id, distance))

            # Sort by distance and assign to the nearest available salesperson
            salesperson_distances.sort(key=lambda x: x[1])
            assigned_salesperson_id = salesperson_distances[0][0]

            # Insert the task into Tasks table
            cursor.execute("""
                INSERT INTO Tasks (CustomerName, PhoneNumber, Latitude, Longitude, AssignedSalespersonId) 
                VALUES (?, ?, ?, ?, ?)
            """, (customer_name, phone_number, latitude, longitude, assigned_salesperson_id))
            conn.commit()
            return True
        except pyodbc.Error as e:
            print("Error assigning task to salesperson: ", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    return False

# Route to complete a task
@app.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Move the task from Tasks table to CompletedTasks table
            cursor.execute("""
                INSERT INTO CompletedTasks (TaskId, CustomerName, PhoneNumber, Latitude, Longitude, SalespersonID)
                SELECT TaskId, CustomerName, PhoneNumber, Latitude, Longitude, SalespersonID 
                FROM Tasks WHERE TaskId = ?
            """, (task_id,))

            # Remove the task from the Tasks table
            cursor.execute("DELETE FROM Tasks WHERE TaskId = ?", (task_id,))

            conn.commit()
            return jsonify({'message': 'Task completed successfully!'})
        except pyodbc.Error as e:
            print("Error completing task: ", e)
            conn.rollback()
            return jsonify({'error': 'Failed to complete task'}), 500
        finally:
            conn.close()
    return jsonify({'error': 'Database connection failed'}), 500

# Configure SQLAlchemy
engine = create_engine('mssql+pyodbc://RAMESH\\SQLEXPRESS/sales3?driver=ODBC+Driver+17+for+SQL+Server')
Session = sessionmaker(bind=engine)


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return distance


@app.route('/next_customer', methods=['GET', 'POST'])
def next_customer():
    if request.method == 'POST':
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        user_id = session.get('user_id')

        if not user_id:
            return jsonify({'message': 'User not logged in.'}), 401

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()

                # Fetch the last recorded location of the logged-in salesperson
                cursor.execute("""
                    SELECT TOP 1 Latitude, Longitude
                    FROM CustomerDetails
                    WHERE SalespersonId = ?
                    ORDER BY CreatedAt DESC
                """, (user_id,))
                salesperson_location = cursor.fetchone()

                if not salesperson_location:
                    return jsonify({'message': 'No location data found for the salesperson.'}), 404

                lat, lon = salesperson_location

                # Fetch all customer tasks based on proximity
                cursor.execute("""
                    SELECT TaskId, CustomerName, PhoneNumber,
                           Latitude, Longitude,
                           (6371 * acos(cos(radians(?)) * cos(radians(Latitude)) * 
                           cos(radians(Longitude) - radians(?)) + sin(radians(?)) * 
                           sin(radians(Latitude)))) AS distance
                    FROM Tasks
                    WHERE AssignedSalespersonId = ?
                    ORDER BY distance ASC
                """, (lat, lon, lat, user_id))
                tasks = cursor.fetchall()

                if tasks:
                    task_list = []
                    for task in tasks:
                        task_id, customer_name, phone_number, latitude, longitude, distance = task
                        task_list.append({
                            'task_id': task_id,
                            'customer_name': customer_name,
                            'phone_number': phone_number,
                            'latitude': latitude,
                            'longitude': longitude,
                            'distance': distance
                        })
                    return jsonify(task_list)
                else:
                    return jsonify({'message': 'No tasks available.'})

            except pyodbc.Error as e:
                print(f"Error: {e}")
                return jsonify({'message': 'An error occurred while fetching the tasks.'}), 500
            
            finally:
                conn.close()

        return jsonify({'message': 'Database connection failed.'}), 500

    # GET method logic
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('index'))

    return render_template('task_page.html')

@app.route('/map_view', methods=['GET'])
def map_view():
    task_id = request.args.get('task_id')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    return render_template('map_view.html', task_id=task_id, latitude=latitude, longitude=longitude)


# Route to receive location updates from the user
@app.route('/update_location', methods=['POST'])
def update_location():
    data = request.get_json()
    salesperson_id = data.get('salesperson_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not salesperson_id or not latitude or not longitude:
        return jsonify({'error': 'Missing data'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert the new location into the database
        query = """
        INSERT INTO SalespersonLocation (SalespersonID, Latitude, Longitude, Timestamp)
        VALUES (?, ?, ?, GETDATE())
        """
        cursor.execute(query, salesperson_id, latitude, longitude)
        conn.commit()
        conn.close()

        return jsonify({'status': 'Location updated successfully'}), 200

    except Exception as e:
        print(f"Error updating location: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)

