from flask import Flask, request, jsonify, render_template,redirect,url_for,flash,session,session
import pyodbc

app = Flask(__name__)
app.secret_key = '123'

# Database connection parameters
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-EOMGEUU\SQLEXP;"
    "USERNAME=sa;"
    "PASSWORD=123;"
    "DATABASE=project1;"
    "Trusted_Connection=yes;"
)

def get_db_connection():
    conn = pyodbc.connect(conn_str)
    return conn

def manager_id():
    username = session.get('username')
    password = session.get('password')
    role = session.get('role')  # Assuming role is also stored in the session

    conn = get_db_connection()
    cursor = conn.cursor()
                
    cursor.execute("SELECT user_id FROM login_page WHERE username = ? AND pass_word = ? AND position = ?", (username, password, role))
    user = cursor.fetchone()

    if user:
        user_id = user[0]  # Extract user_id from the fetched tuple
        cursor.execute("SELECT Dept_Id FROM emp_status WHERE user_id = ?", (user_id,))
        user1 = cursor.fetchone()

        if user1:
            return int(user1[0])  # Return the department ID
        else:
            return None  # No department ID found for the given user_id
    else:
        return None  # No user found with the given credentials

    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    session['username'] = username
    session['password'] = password
    session['role'] = role

    if not username or not password or not role:
        return render_template('index.html', error_message='All fields are required.')
    
    try:
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT position FROM login_page WHERE username = ? AND pass_word = ? AND position = ?", (username, password, role))
        
        user = cursor.fetchone()
        
        if user:
            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'manager':
                return redirect(url_for('manager_dashboard'))
            elif role == 'employee':
                return redirect(url_for('employee_dashboard'))
        else:
            return render_template('index.html', error_message='Invalid credentials or role.')
        
    except pyodbc.Error as e:
        print(f"Database error: {e}")
        return render_template('index.html', error_message='Database connection failed. Please check your settings.')
    except Exception as e:
        print(f"Error: {e}")
        return render_template('index.html', error_message='An unexpected error occurred. Please try again later.')
    
    finally:
        cursor.close()
        conn.close()


@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/manager_dashboard')
def manager_dashboard():
    return render_template('manager_dashboard.html')

@app.route('/employee_dashboard')
def employee_dashboard():
    return render_template('employee_dashboard.html')


@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        employee_name = request.form['employeeName']
        department_id = request.form['employeeDepartmentId']

        if not department_id.isdigit():
            return "Invalid department ID. Please provide a numeric value.", 400
        
        department_id = int(department_id)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if the employee already exists
            query = "SELECT * FROM Employees WHERE employeeName = ? AND employeeDepartmentId = ?"
            cursor.execute(query, (employee_name, department_id))
            result = cursor.fetchone()

            if result:
                return "Sorry, the data already exists."

            # Insert the new employee
            cursor.execute(
                "INSERT INTO Employees (EmployeeName, EmployeeDepartmentID) VALUES (?, ?)",
                (employee_name, department_id)
            )
            conn.commit()
            return "Successfully added."

        except Exception as e:
            print(f"Database error: {e}")
            return "An error occurred while adding the employee.", 500

        finally:
            conn.close()

    return render_template('add_employee.html')

@app.route('/assign_task')
def assign_task():
    return render_template('assign_task.html')


@app.route('/submit_task', methods=['GET', 'POST'])
def submit_task():
    if request.method == 'POST':
        try:
            # If data comes from a form submission, use request.form
            task_name = request.form.get('taskName')
            assign_to = request.form.get('assignTo')
            department_Id = request.form.get('departmentId')
            deadline_date = request.form.get('deadlineDate')

            # Establish database connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Corrected SQL query with four placeholders
            cursor.execute("INSERT INTO Tasks (TaskName, EmployeeID, DepartmentID, DeadlineDate) VALUES (?, ?, ?, ?)",
                           (task_name, assign_to, department_Id, deadline_date))
            
            # Commit the transaction
            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({'message': 'Task assigned successfully'}), 200

        except pyodbc.DatabaseError as db_err:
            print(f"Database error occurred: {db_err}")
            return jsonify({'error': 'Database error occurred'}), 500
        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({'error': 'An error occurred'}), 500

    # Optionally, handle GET requests if needed
    return jsonify({'message': 'Use POST to submit data'}), 405

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        position = request.form['position']

        # Insert data into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO login_page (username, Pass_word, Position)
            VALUES (?, ?, ?)
        """, (username, password, position))
        conn.commit()
        conn.close()

        return redirect(url_for('signup_success'))

    return render_template('signup.html')

@app.route('/signup_success')
def signup_success():
    return "Signup successful!"

@app.route('/update_status', methods=['POST'])
def update_status():
    try:
        project_id = request.form.get('projectId')
        project_name = request.form.get('projectName')
        status = request.form.get('status')
        remarks = request.form.get('remarks')

        if not project_id or not project_name or not status:
            flash('Project ID, Project Name, and Status are required.', 'error')
            return redirect(url_for('home'))

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Projects (ProjectID, ProjectName, Status, Remarks)
            VALUES (?, ?, ?, ?)
        """, (project_id, project_name, status, remarks))
        conn.commit()

        flash('Project status updated successfully!', 'success')
        return redirect(url_for('home'))

    except Exception as e:
        flash('An error occurred. Please try again later.', 'error')
        return redirect(url_for('home'))

    finally:
        cursor.close()
        conn.close()


@app.route('/attendance', methods=['GET', 'POST'])
def record_attendance():
    if request.method == 'POST':
        employee_id = request.form.get('employeeId')
        department_id = request.form.get('departmentId')
        date = request.form.get('date')
        status = request.form.get('status')
        
        # Check if any form field is missing
        if not employee_id or not department_id or not date or not status:
            return "Error: All fields are required.", 400
        
        # Connect to the database and insert the data
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Attendance (EmployeeID, DepartmentID, AttendanceDate, Status)
                VALUES (?, ?, ?, ?)
            """, (employee_id, department_id, date, status))
            conn.commit()
        except Exception as e:
            print(f"Error: {e}")
            return "An error occurred while recording attendance.", 500
        finally:
            conn.close()
        
        return render_template('attendance.html')
    else:
        return render_template('attendance.html')




@app.route('/project_status', methods=['GET', 'POST'])
def project_status():
    if request.method == 'POST':
        project_name = request.form['projectName']
        start_date = request.form['startDate']
        end_date = request.form['endDate']
        status = request.form['status']
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO ProjectStatus (ProjectName, StartDate, EndDate, Status) VALUES (?, ?, ?, ?)", 
                    (project_name, start_date, end_date, status)
                )
                conn.commit()
                cursor.close()
            except pyodbc.Error as e:
                print("Error executing query:", e)
            finally:
                conn.close()
        return redirect('/project_status')
    return render_template('project_status.html')




#get methods


@app.route('/get_employee')
def get_employee_form():
    return render_template('get_employee.html', error=None, employee=None)

@app.route('/fetch_employee', methods=['POST'])
def fetch_employee():
    employee_id = request.form.get('employeeId')
    
    if not employee_id:
        return render_template('get_employee.html', error='Employee ID is required.', employee=None)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT EmployeeID, EmployeeName, EmployeeDepartmentId FROM Employees WHERE EmployeeID = ?", (employee_id,))
        
        employee = cursor.fetchone()
        
        if not employee:
            return render_template('get_employee.html', error='No employee found with this ID.', employee=None)
        
        return render_template('get_employee.html', error=None, employee=employee)
    
    except Exception as e:
        print(f"Error: {e}")  # Log error for debugging
        return render_template('get_employee.html', error='An error occurred. Please try again later.', employee=None)
    
    finally:
        cursor.close()
        conn.close()


#fetch all

@app.route('/fetch_all_employees')
def fetch_all_employees():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT EmployeeID, EmployeeName, EmployeeDepartmentId FROM Employees")
        all_employees = cursor.fetchall()
        
        return render_template('get_employee.html', error=None, employee=None, all_employees=all_employees)
    
    except Exception as e:
        print(f"Error: {e}")  # Log error for debugging
        return render_template('get_employee.html', error='An error occurred. Please try again later.', employee=None, all_employees=None)
    
    finally:
        cursor.close()
        conn.close()



#delete emp username and password

@app.route('/delete_employee', methods=['GET', 'POST'])
def delete_employee():
    if request.method == 'POST':
        employee_id = request.form['employee_id']

        try:
            with pyodbc.connect(conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Tasks WHERE AssignedTo = ?", employee_id)
                cursor.execute("DELETE FROM Employees WHERE EmployeeId = ?", employee_id)
                conn.commit()
            return "Employee deleted successfully!"
        except Exception as e:
            return f"An error occurred: {e}"
    
    return render_template('delete_employee.html')



#---------------------------------

 

@app.route('/assign_task1', methods=['GET', 'POST'])
def assign_task1():
    if request.method == 'POST':
        manager_id = request.form.get('manager_id')
        if not manager_id:
            return "Manager ID is required.", 400  # Bad Request
        
        try:
            manager_id = int(manager_id)
        except ValueError:
            return "Invalid Manager ID.", 400
        
        department_id = get_manager_department_id(manager_id)
        if department_id:
            # Handle the task assignment logic here
            return f"Manager's Department ID is {department_id}"
        else:
            return "Manager not found or no department assigned.", 404  # Not Found
    return render_template('assign_task1.html')



@app.route('/manage_attendance', methods=['GET', 'POST'])
def manage_attendance():
    if request.method == 'POST':
        employee_id = request.form.get('employeeId')
        department_id = request.form.get('departmentId')
        date = request.form.get('date')
        status = request.form.get('status')

        # Assuming the manager's department ID is stored in the session or can be determined from the logged-in user
        manager_department_id = manager_id()  # Example: 101

        # Check if any form field is missing
        if not employee_id or not department_id or not date or not status:
            return "Error: All fields are required.", 400

        # Validate that the manager is only adding attendance for their department
        if int(department_id) != int(manager_department_id):
            return "Error: You can only add attendance for your department.", 403

        # Connect to the database and insert the data
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Attendance (EmployeeID, DepartmentID, AttendanceDate, Status)
                VALUES (?, ?, ?, ?)
            """, (employee_id, department_id, date, status))
            conn.commit()
        except Exception as e:
            print(f"Error: {e}")
            return "An error occurred while recording attendance.", 500
        finally:
            conn.close()
        
        return "Attendance recorded successfully.", 200

    # Handle GET request or other logic if necessary
    return render_template('manage_attendance.html')


@app.route('/submit_task1', methods=['GET', 'POST'])
def submit_task1():
    if request.method == 'POST':
        task_name = request.form.get('taskName')
        assign_to = request.form.get('assignTo')
        department_id = request.form.get('departmentId')
        deadline_date = request.form.get('deadlineDate')

        manager_department_id = manager_id()  

        # Check if any form field is missing
        if not task_name or not department_id or not department_id or not deadline_date:
            return "Error: All fields are required.", 400

        # Validate that the manager is only adding attendance for their department
        if int(department_id) != int(manager_department_id):
            return "Error: You can only add attendance for your department.", 403
        
        try:

            # Establish database connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Corrected SQL query with four placeholders
            cursor.execute("INSERT INTO Tasks (TaskName, EmployeeID, DepartmentID, DeadlineDate) VALUES (?, ?, ?, ?)",
                           (task_name, assign_to, department_id, deadline_date))
            
            # Commit the transaction
            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({'message': 'Task assigned successfully'}), 200

        except pyodbc.DatabaseError as db_err:
            print(f"Database error occurred: {db_err}")
            return jsonify({'error': 'Database error occurred'}), 500
        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({'error': 'An error occurred'}), 500

    # Optionally, handle GET requests if needed
    return jsonify({'message': 'Use POST to submit data'}), 405


@app.route('/add_employee1', methods=['GET', 'POST'])
def add_employee1():
    if request.method == 'POST':
        employee_name = request.form['employeeName']
        department_id = request.form['employeeDepartmentId']

        manager_department_id = manager_id()

        if int(department_id) != int(manager_department_id):
            return "Error: You can only add attendance for your department.", 403
        
        # Convert department_id to integer if it's not already
        try:
            department_id = int(department_id)
        except ValueError:
            return "Invalid Department ID", 400

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Employees (EmployeeName, EmployeeDepartmentId) VALUES (?, ?)",
                    (employee_name, department_id)
                )
                conn.commit()
            except Exception as e:
                print(f"Database insertion error: {e}")
                return "An error occurred while adding the employee.", 500
            finally:
                conn.close()
            return ('successfully added')
            return redirect(url_for('add_employee1'))
        else:
            return "Database connection error", 500

    return render_template('add_employee1.html')


@app.route('/get_employee1')
def get_employee1():
    return render_template('get_employee1.html', error=None, employee=None)

@app.route('/fetch_employee1', methods=['POST'])
def fetch_employee1():
    employee_id = request.form.get('employeeId')

    manager_department_id = manager_id()
    
    if not employee_id:
        return render_template('get_employee1.html', error='Employee ID is required.', employee=None)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT EmployeeID, EmployeeName, EmployeeDepartmentId FROM Employees WHERE EmployeeID = ? and EmployeeDepartmentId = ?", (employee_id,manager_department_id,))
        employee = cursor.fetchone()
        
        if not employee:
            return render_template('get_employee1.html', error='No employee found with this ID.', employee=None)
        
        return render_template('get_employee1.html', error=None, employee=employee)
    
    except Exception as e:
        print(f"Error: {e}")  # Log error for debugging
        return render_template('get_employee1.html', error='An error occurred. Please try again later.', employee=None)
    
    finally:
        cursor.close()
        conn.close()

@app.route('/fetch_all_employees1')
def fetch_all_employees1():
    manager_department_id = manager_id()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT EmployeeID, EmployeeName, EmployeeDepartmentId FROM Employees where EmployeeDepartmentId = ?",(manager_department_id,))
        all_employees = cursor.fetchall()
        
        return render_template('get_employee1.html', error=None, employee=None, all_employees=all_employees)
    
    except Exception as e:
        print(f"Error: {e}")  # Log error for debugging
        return render_template('get_employee1.html', error='An error occurred. Please try again later.', employee=None, all_employees=None)
    
    finally:
        cursor.close()
        conn.close()


#-------------------------------------------

#employees

@app.route('/emp_attendance')
def emp_attendance():
    emp_department_id = manager_id()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT EmployeeID, DepartmentID, AttendanceDate, Status FROM Attendance where DepartmentID = ?",(emp_department_id))
        all_employees = cursor.fetchall()
        
        return render_template('emp_attendance.html',rows = all_employees)
    
    except Exception as e:
        print(f"Error: {e}")  # Log error for debugging
        return render_template('emp_attendance.html', error='An error occurred. Please try again later.', employee=None, all_employees=None)
    
    finally:
        cursor.close()
        conn.close()


@app.route('/emp_task')
def emp_task():
    emp_department_id = manager_id()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT TaskName, EmployeeID, DepartmentID, DeadlineDate FROM Tasks where DepartmentID = ?",(emp_department_id))
        all_employees = cursor.fetchall()
        
        return render_template('emp_task.html',rows = all_employees)
    
    except Exception as e:
        print(f"Error: {e}")  # Log error for debugging
        return render_template('emp_task.html', error='An error occurred. Please try again later.', employee=None, all_employees=None)
    
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
