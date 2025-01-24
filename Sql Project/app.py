from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = '123'  # Secret key for flash messages

# Function to get the MySQL connection using credentials stored in the session
def get_connection(database=None):
    db_config = {
        'host': session.get('hostname', 'localhost'),
        'user': session.get('username', 'root'),
        'password': session.get('password', ''),
        'database': database
    }
    try:
        return mysql.connector.connect(**db_config)
    except Error as err:
        flash(f"Connection error: {err}", "danger")
        return None

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    hostname = request.form.get('hostname')
    username = request.form.get('username')
    password = request.form.get('password')

    # Store the credentials in the session for future database connections
    session['hostname'] = hostname
    session['username'] = username
    session['password'] = password

    connection = get_connection()
    if connection and connection.is_connected():
        flash("Connected Successfully!", "success")
        connection.close()
        return redirect(url_for('index'))
    else:
        return redirect(url_for('home'))

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/go_to_create_database')
def go_to_create_database():
    return render_template('create_database.html')

@app.route('/create_database', methods=['POST'])
def create_database():
    db_name = request.form['db_name']
    try:
        connection = get_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE {db_name}")
            flash(f"Database '{db_name}' created successfully!", 'success')
            cursor.close()
            connection.close()
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'danger')
    return redirect(url_for('index'))

@app.route('/go_to_create_table')
def go_to_create_table():
    try:
        connection = get_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            cursor.close()
            connection.close()
            return render_template('create_table.html', databases=databases)
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'danger')
    return redirect(url_for('index'))

@app.route('/create_table', methods=['POST'])
def create_table():
    db_name = request.form['db_name']
    table_name = request.form['table_name']
    columns = []

    # Retrieve column names and types from the form
    i = 1
    while f'column_name_{i}' in request.form:
        column_name = request.form[f'column_name_{i}']
        column_type = request.form[f'column_type_{i}']
        columns.append(f"{column_name} {column_type}")
        i += 1

    columns_sql = ", ".join(columns)
    try:
        connection = get_connection(database=db_name)
        if connection:
            cursor = connection.cursor()
            cursor.execute(f"CREATE TABLE {table_name} ({columns_sql})")
            flash(f"Table '{table_name}' created successfully in database '{db_name}'!", 'success')
            cursor.close()
            connection.close()
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'danger')
    return redirect(url_for('index'))

@app.route('/get_databases')
def get_databases():
    try:
        connection = get_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            cursor.close()
            connection.close()
            return jsonify(databases)
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

@app.route('/get_tables')
def get_tables():
    database = request.args.get('database')
    if not database:
        return jsonify({'error': 'No database specified'}), 400

    try:
        connection = get_connection(database=database)
        if connection:
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            cursor.close()
            connection.close()
            return jsonify(tables)
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

@app.route('/get_columns')
def get_columns():
    database = request.args.get('database')
    table = request.args.get('table')
    if not database or not table:
        return jsonify({'error': 'Database or table not specified'}), 400

    try:
        connection = get_connection(database=database)
        if connection:
            cursor = connection.cursor()
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            columns = [row[0] for row in cursor.fetchall()]
            cursor.close()
            connection.close()
            return jsonify({'columns': columns})
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

@app.route('/perform_delete', methods=['POST'])
def perform_delete():
    delete_type = request.form.get('delete_type')
    name = request.form.get('database_name') or request.form.get('table_name')

    try:
        if delete_type == 'database':
            connection = get_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute(f"DROP DATABASE {name}")
                flash(f"Database '{name}' deleted successfully!", 'success')
                cursor.close()
                connection.close()

        elif delete_type == 'table':
            database = request.form.get('database_name')
            if not database:
                flash("No database selected", 'danger')
                return redirect(url_for('go_to_delete'))

            connection = get_connection(database=database)
            if connection:
                cursor = connection.cursor()
                cursor.execute(f"DROP TABLE {name}")
                flash(f"Table '{name}' deleted successfully from database '{database}'!", 'success')
                cursor.close()
                connection.close()
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'danger')
    return redirect(url_for('go_to_delete'))

@app.route('/go_to_delete')
def go_to_delete():
    return render_template('delete.html')

@app.route('/insert_data', methods=['POST'])
def insert_data():
    database = request.form.get('database')
    table = request.form.get('table')
    data = request.form.to_dict()
    data.pop('database', None)
    data.pop('table', None)

    columns = ', '.join(data.keys())
    placeholders = ', '.join(['%s' for _ in data.values()])
    values = list(data.values())

    try:
        connection = get_connection(database=database)
        if connection:
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
            flash('Data inserted successfully!', 'success')
            cursor.close()
            connection.close()
    except mysql.connector.Error as err:
        flash(f'Error inserting data: {err}', 'danger')
    return redirect(url_for('go_to_insert'))

@app.route('/go_to_insert')
def go_to_insert():
    return render_template('insert.html')

@app.route('/go_to_joins', methods=['GET', 'POST'])
def go_to_joins():
    result = None
    error_message = None

    try:
        connection = get_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            cursor.close()
            connection.close()
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'danger')
        databases = []

    selected_database = request.args.get('database') or request.form.get('database')

    if request.method == 'POST':
        join_type = request.form.get('join_type')
        selected_tables = request.form.getlist('tables[]')
        selected_columns1 = request.form.getlist('columns_table1[]')
        selected_columns2 = request.form.getlist('columns_table2[]')

        if len(selected_tables) < 2 or len(selected_columns1) < 1 or len(selected_columns2) < 1:
            error_message = "Please select at least two tables and one column from each table for the join operation."
        else:
            try:
                connection = get_connection(database=selected_database)
                if connection:
                    cursor = connection.cursor()

                    # Assign aliases to the tables
                    table1, table2 = selected_tables[0], selected_tables[1]
                    column1, column2 = selected_columns1[0], selected_columns2[0]

                    # Modify the join query to include table aliases
                    query = f"""
                    SELECT * 
                    FROM {table1} AS t1 
                    {join_type} {table2} AS t2 
                    ON t1.{column1} = t2.{column2}
                    """

                    cursor.execute(query)
                    result = cursor.fetchall()
                    columns = cursor.column_names
                    cursor.close()
                    connection.close()
            except mysql.connector.Error as err:
                error_message = f"Error performing join: {err}"

    return render_template('select_join.html', databases=databases, selected_database=selected_database, result=result, error_message=error_message, join_types=['INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL OUTER JOIN'])

@app.route('/fetch_tables', methods=['POST'])
def fetch_tables():
    database = request.json.get('database')
    tables = []

    if database:
        try:
            connection = get_connection(database=database)
            if connection:
                cursor = connection.cursor()
                cursor.execute("SHOW TABLES")
                tables = [table[0] for table in cursor.fetchall()]
                cursor.close()
                connection.close()
        except mysql.connector.Error as err:
            return jsonify({'error': str(err)})

    return jsonify({'tables': tables})

@app.route('/fetch_columns', methods=['POST'])
def fetch_columns():
    table = request.json.get('table')
    database = request.json.get('database')
    columns = []

    if table and database:
        try:
            connection = get_connection(database=database)
            if connection:
                cursor = connection.cursor()
                cursor.execute(f"SHOW COLUMNS FROM {table}")
                columns = [column[0] for column in cursor.fetchall()]
                cursor.close()
                connection.close()
        except mysql.connector.Error as err:
            return jsonify({'error': str(err)})

    return jsonify({'columns': columns})

if __name__ == '__main__':
    app.run(debug=True)
