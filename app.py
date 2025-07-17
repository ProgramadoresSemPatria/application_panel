from flask import Flask, request, render_template, redirect, url_for, flash, session, abort
import sqlite3

app = Flask(__name__)

def get_database_connection():
    """
    Creates and returns a database connection.
    This function should be called whenever you need to interact with the database.
    """
    con = sqlite3.connect("database.db")

    # Enable foreign key constraints in SQLite
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def create_database_schema():
    """
    Creates all tables needed for the job application tracking system.
    Tables are created in dependency order to handle foreign key relationships.
    """

    # Create a connection specifically for schema creation
    con = get_database_connection()
    cur = con.cursor()

    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS platforms (
                platform_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT, 
                url TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                application_id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_date DATETIME,
                company TEXT,
                role TEXT,
                platform_id INTEGER,
                salary_range_min INTEGER,
                salary_range_max INTEGER,
                expected_salary INTEGER,
                salary_offer INTEGER,
                last_step INTEGER,
                last_step_date DATETIME,
                mode TEXT,
                feedback_id INTEGER,
                feedback_date DATETIME,
                observation TEXT,
                FOREIGN KEY (platform_id) REFERENCES platforms(platform_id),
                FOREIGN KEY (feedback_id) REFERENCES feedbacks_definition(feedback_id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER,
                step INTEGER,
                step_observation TEXT,
                step_date DATETIME,
                FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE CASCADE,
                FOREIGN KEY (step) REFERENCES steps_definition(step)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS steps_definition (
                step INTEGER PRIMARY KEY,
                step_name TEXT,
                step_description TEXT,
                step_color TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedbacks_definition (
                feedback_id INTEGER PRIMARY KEY,
                feedback_name TEXT,
                feedback_description TEXT, 
                feedback_color TEXT
            )
        """)

        # Commit all the table creations
        con.commit()
        print("Database schema created successfully!")
        
    except sqlite3.Error as e:
        print(f"Error creating database schema: {e}")
        con.rollback()
    finally:
        con.close()

def insert_example():
    con = get_database_connection()
    cur = con.cursor()

    cur.execute("INSERT INTO platforms (name, url) VALUES ('Linkedin', 'https://linkedin.com')")
    cur.execute("INSERT INTO feedbacks_definition (feedback_name, feedback_description, feedback_color) VALUES ('Assessment failed', 'Assessment failed description', '#ffffff')")
    cur.execute("INSERT INTO applications (application_date, company, role, platform_id, salary_range_min, salary_range_max, expected_salary, salary_offer, last_step, last_step_date, mode, feedback_id, feedback_date, observation) VALUES ('2025-07-16', 'Company Test', 'Data Engineer', 1, 50, 100, 60, 50, 6, '2025-07-16', 'pasive', 1, '2025-07-16', 'test application')")
    con.commit()
    con.close()

@app.route('/applications/<int:application_id>', methods=['GET'])
def view_application(application_id):
    con = get_database_connection()
    cur = con.cursor()

    cur.execute("SELECT * FROM applications WHERE application_id = ?", [application_id])
    application = cur.fetchone()

    if application is None:
        con.close()
        return render_template('application_not_found.html'), 404
    
    con.close()
    return render_template('application_detail.html', application=application)

@app.route('/platforms', methods=['GET', 'POST'])
def platforms():
    if request.method == "GET":
        con = get_database_connection()
        cur = con.cursor()

        cur.execute("SELECT * FROM platforms")
        platforms = cur.fetchall()
        con.close()
        return render_template('platforms.html', platforms=platforms)
    
    if request.method == "POST":
        name = request.form.get('platform_name')
        url = request.form.get('platform_url')

        con = get_database_connection()
        cur = con.cursor()

        cur.execute("INSERT INTO platforms (name, url) VALUES(?, ?)", (name, url))
        con.commit()
        con.close()
        return redirect(url_for('platforms'))

@app.route('/platforms/<int:platform_id>/delete', methods=['POST'])
def delete_platform(platform_id):

    con = get_database_connection()
    cur = con.cursor()

    cur.execute("DELETE FROM applications WHERE platform_id = ?", [platform_id])
    cur.execute("DELETE FROM platforms WHERE platform_id = ?", [platform_id])
    con.commit()
    con.close()
    return redirect(url_for('platforms'))

@app.route('/platforms/<int:platform_id>/update', methods=['POST'])
def update_platform(platform_id):

    name = request.form.get('platform_name')
    url = request.form.get('platform_url')

    con = get_database_connection()
    cur = con.cursor()

    cur.execute("UPDATE SET name = ?, url = ? FROM platforms WHERE platform_id = ?", (name, url, platform_id))
    con.commit()
    con.close()
    return redirect(url_for('platforms'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)