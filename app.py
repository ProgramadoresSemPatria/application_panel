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
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT, 
                url TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                FOREIGN KEY (platform_id) REFERENCES platforms(id),
                FOREIGN KEY (feedback_id) REFERENCES feedbacks_definition(id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER,
                step_id INTEGER,
                observation TEXT,
                step_date DATETIME,
                FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
                FOREIGN KEY (step_id) REFERENCES steps_definition(id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS steps_definition (
                id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT,
                color TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedbacks_definition (
                id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT, 
                color TEXT
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

    #cur.execute("INSERT INTO platforms (name, url) VALUES ('Linkedin', 'https://linkedin.com')")
    #cur.execute("INSERT INTO feedbacks_definition (name, description, color) VALUES ('Assessment failed', 'Assessment failed description', '#ffffff')")
    #cur.execute("INSERT INTO steps_definition (id, name, description, color) VALUES (1, 'Application Submitted', 'Initial application submitted to company', '#3498db')")
    cur.execute("INSERT INTO applications (application_date, company, role, platform_id, salary_range_min, salary_range_max, expected_salary, salary_offer, last_step, last_step_date, mode, feedback_id, feedback_date, observation) VALUES ('2025-07-16', 'Company FULL', 'Data Scientist', 1, 50, 100, 60, 50, 1, '2025-07-16', 'pasive', 1, '2025-07-16', 'test application')")
    cur.execute("INSERT INTO steps (application_id, step_id, observation, step_date) VALUES (1, 1, 'Applied through company website', '2025-07-10')")
    con.commit()
    con.close()

@app.route('/applications/<int:application_id>', methods=['GET'])
def view_application(application_id):
    con = get_database_connection()
    cur = con.cursor()

    cur.execute("SELECT * FROM applications WHERE id = ?", [application_id])
    application = cur.fetchone()

    if application is None:
        con.close()
        return render_template('application_not_found.html'), 404
    
    con.close()
    return render_template('application_detail.html', application=application)

@app.route('/applications', methods=['GET', 'POST'])
def applications():
    if request.method == "GET":
        con = get_database_connection()
        cur = con.cursor()

        cur.execute("SELECT * FROM applications")
        applications = cur.fetchall()

        cur.execute("SELECT * FROM platforms")
        platforms = cur.fetchall()

        cur.execute("SELECT * FROM steps_definition")
        steps_definition = cur.fetchall()

        cur.execute("SELECT * FROM feedbacks_definition")
        feedbacks_definition = cur.fetchall()

        con.close()
        return render_template('applications.html', applications=applications, platforms=platforms, steps_definition=steps_definition, feedbacks_definition=feedbacks_definition)
    
    if request.method == "POST":
        name = request.form.get('platform_name')
        url = request.form.get('platform_url')

        con = get_database_connection()
        cur = con.cursor()

        cur.execute("INSERT INTO applications (name, url) VALUES(?, ?)", (name, url))
        con.commit()
        con.close()
        return redirect(url_for('applications'))

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

@app.route('/platforms/<int:platform_id>/check_applications', methods=['GET'])
def check_platform_applications(platform_id):
    con = get_database_connection()
    cur = con.cursor()
    
    cur.execute("SELECT COUNT(*) FROM applications WHERE platform_id = ?", [platform_id])
    count = cur.fetchone()[0]
    
    con.close()
    return {'count': count}

@app.route('/platforms/<int:platform_id>/update', methods=['POST'])
def update_platform(platform_id):

    name = request.form.get('platform_name')
    url = request.form.get('platform_url')

    con = get_database_connection()
    cur = con.cursor()

    cur.execute("UPDATE platforms SET name = ?, url = ? WHERE id = ?", (name, url, platform_id))
    con.commit()
    con.close()
    return redirect(url_for('platforms'))

@app.route('/platforms/<int:platform_id>/delete', methods=['POST'])
def delete_platform(platform_id):

    con = get_database_connection()
    cur = con.cursor()

    cur.execute("DELETE FROM applications WHERE platform_id = ?", [platform_id])
    cur.execute("DELETE FROM platforms WHERE id = ?", [platform_id])
    con.commit()
    con.close()
    return redirect(url_for('platforms'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == "GET":
        con = get_database_connection()
        cur = con.cursor()

        cur.execute("SELECT * FROM feedbacks_definition")
        feedbacks = cur.fetchall()

        cur.execute("SELECT * FROM steps_definition")
        steps = cur.fetchall()

        con.close()
        return render_template('settings.html', feedbacks=feedbacks, steps=steps)
    
    if request.method == "POST":

        form_type = request.form.get('form_type')
        if form_type == 'create_step_defition':

            name = request.form.get('step_name')
            description = request.form.get('step_description')
            color = request.form.get('step_color')

            con = get_database_connection()
            cur = con.cursor()

            cur.execute("INSERT INTO steps_definition (name, description, color) VALUES(?, ?, ?)", (name, description, color))
            con.commit()
            con.close()
            return redirect(url_for('settings'))

        elif form_type == 'create_feedback_defition':

            name = request.form.get('feedback_name')
            description = request.form.get('feedback_description')
            color = request.form.get('feedback_color')

            con = get_database_connection()
            cur = con.cursor()

            cur.execute("INSERT INTO feedbacks_definition (name, description, color) VALUES(?, ?, ?)", (name, description, color))
            con.commit()
            con.close()
            return redirect(url_for('settings'))

@app.route('/settings/steps/<int:step_id>/check_applications', methods=['GET'])
def check_steps_applications(step_id):
    con = get_database_connection()
    cur = con.cursor()
    
    cur.execute("SELECT COUNT(DISTINCT application_id) FROM steps WHERE step_id = ?", [step_id])
    count = cur.fetchone()[0]
    
    con.close()
    return {'count': count}

@app.route('/settings/steps/<int:step_id>/update', methods=['POST'])
def update_step_definition(step_id):

    name = request.form.get('step_name')
    description = request.form.get('step_description')
    color = request.form.get('step_color')

    con = get_database_connection()
    cur = con.cursor()

    cur.execute("UPDATE steps_definition SET name = ?, description = ?, color = ? WHERE id = ?", (name, description, color, step_id))
    con.commit()
    con.close()
    return redirect(url_for('settings'))

@app.route('/settings/steps/<int:step_id>/delete', methods=['POST'])
def delete_step_definition(step_id):

    con = get_database_connection()
    cur = con.cursor()

    cur.execute("DELETE FROM applications WHERE id IN (SELECT application_id FROM steps WHERE step_id = ?)", [step_id])
    cur.execute("DELETE FROM steps_definition WHERE id = ?", [step_id])
    con.commit()
    con.close()
    return redirect(url_for('settings'))

@app.route('/settings/feedbacks/<int:feedback_id>/check_applications', methods=['GET'])
def check_feedbacks_applications(feedback_id):
    con = get_database_connection()
    cur = con.cursor()
    
    cur.execute("SELECT COUNT(*) FROM applications WHERE feedback_id = ?", [feedback_id])
    count = cur.fetchone()[0]
    
    con.close()
    return {'count': count}

@app.route('/settings/feedbacks/<int:feedback_id>/update', methods=['POST'])
def update_feedback_definition(feedback_id):

    name = request.form.get('feedback_name')
    description = request.form.get('feedback_description')
    color = request.form.get('feedback_color')

    con = get_database_connection()
    cur = con.cursor()

    cur.execute("UPDATE feedbacks_definition SET name = ?, description = ?, color = ? WHERE id = ?", (name, description, color, feedback_id))
    con.commit()
    con.close()
    return redirect(url_for('settings'))

@app.route('/settings/feedbacks/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback_definition(feedback_id):

    con = get_database_connection()
    cur = con.cursor()

    cur.execute("DELETE FROM applications WHERE feedback_id = ?", [feedback_id])
    cur.execute("DELETE FROM feedbacks_definition WHERE id = ?", [feedback_id])
    con.commit()
    con.close()
    return redirect(url_for('settings'))

if __name__ == '__main__':
    #create_database_schema()
    #insert_example()
    app.run(debug=True, host='0.0.0.0', port=5000)