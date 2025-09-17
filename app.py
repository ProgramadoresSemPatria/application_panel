from flask import Flask, request, render_template, redirect, url_for, flash, session, abort
import psycopg2
import psycopg2.extras
import os
import hashlib
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://username:password@host:port/database')

def get_database_connection():
    """
    Establishes a connection to the PostgreSQL database.
    
    Returns:
        psycopg2.Connection: Database connection with dict cursor factory
    """
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # Handle potential issues with connection parameters
    try:
        con = psycopg2.connect(DATABASE_URL)
    except psycopg2.OperationalError as e:
        # If there's an issue with channel_binding, try without it
        if 'channel_binding' in str(e) or 'invalid integer value' in str(e):
            # Remove channel_binding parameter if it exists
            clean_url = DATABASE_URL.replace('&channel_binding=require', '').replace('?channel_binding=require', '?sslmode=require')
            con = psycopg2.connect(clean_url)
        else:
            raise e
    
    con.cursor_factory = psycopg2.extras.RealDictCursor
    return con

def hash_password(password):
    """
    Hash a password using SHA-256.
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    """
    Decorator to require login for routes.
    
    Args:
        f: Function to decorate
        
    Returns:
        Function: Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration.
    
    GET: Display registration form
    POST: Process registration form
    
    Returns:
        str: Rendered register.html template or redirect to login
    """
    if request.method == 'GET':
        return render_template('register.html')
    
    if request.method == 'POST':
        # Extract form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        current_company = request.form.get('current_company')
        current_salary = request.form.get('current_salary')
        experience_years = request.form.get('experience_years')
        tech_stack = request.form.get('tech_stack')
        
        # Basic validation
        if not all([username, email, password, confirm_password]):
            flash('Please fill in all required fields.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        con = get_database_connection()
        cur = con.cursor()
        
        try:
            # Check if username or email already exists
            cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            if cur.fetchone():
                flash('Username or email already exists.', 'error')
                return render_template('register.html')
            
            # Hash password and insert user
            hashed_password = hash_password(password)
            cur.execute("""
                INSERT INTO users (username, email, password_hash, first_name, last_name, 
                                 current_company, current_salary, experience_years, tech_stack)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                username, email, hashed_password, first_name, last_name,
                current_company, current_salary, experience_years, tech_stack
            ))
            
            con.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            con.rollback()
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')
        finally:
            con.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    
    GET: Display login form
    POST: Process login form
    
    Returns:
        str: Rendered login.html template or redirect to home
    """
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not all([username, password]):
            flash('Please fill in all fields.', 'error')
            return render_template('login.html')
        
        con = get_database_connection()
        cur = con.cursor()
        
        try:
            # Check user credentials
            hashed_password = hash_password(password)
            cur.execute("""
                SELECT id, username, email, first_name, last_name, is_active 
                FROM users 
                WHERE username = %s AND password_hash = %s AND is_active = true
            """, (username, hashed_password))
            
            user = cur.fetchone()
            
            if user:
                # Set session data
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['email'] = user['email']
                session['first_name'] = user['first_name']
                session['last_name'] = user['last_name']
                
                flash(f'Welcome back, {user["first_name"] or user["username"]}!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password.', 'error')
                return render_template('login.html')
                
        except Exception as e:
            flash('Login failed. Please try again.', 'error')
            return render_template('login.html')
        finally:
            con.close()

@app.route('/logout')
def logout():
    """
    Handle user logout.
    
    Returns:
        Response: Redirect to login page
    """
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@app.route('/home')
@login_required
def home():
    """
    Home dashboard with application analytics and metrics for current user.
    """
    user_id = session.get('user_id')
    
    con = get_database_connection()
    cur = con.cursor()
    
    # Get total applications count for current user
    cur.execute("SELECT COUNT(DISTINCT application_id) as total FROM steps s JOIN applications a ON s.application_id = a.id WHERE a.user_id = %s", (user_id,))
    total_applications = cur.fetchone()['total']

    # Get applications count per step for current user
    cur.execute("""
        SELECT 
            sd.id as step_id,
            sd.name as step_name,
            sd.color as step_color,
            COUNT(DISTINCT s.application_id) as applications_count
        FROM steps_definition sd
        LEFT JOIN steps s ON s.step_id = sd.id
        LEFT JOIN applications a ON a.id = s.application_id AND a.user_id = %s
        GROUP BY sd.id, sd.name, sd.color
        ORDER BY sd.id
    """, (user_id,))
    applications_per_step = cur.fetchall()

    # Calculate conversion rates for each step
    conversion_data = []
    for step in applications_per_step:
        conversion_rate = (
            round((step['applications_count'] / total_applications * 100), 1) 
            if total_applications > 0 else 0
        )
        conversion_data.append({
            'step_id': step['step_id'],
            'step_name': step['step_name'],
            'step_color': step['step_color'],
            'applications_count': step['applications_count'],
            'conversion_rate': conversion_rate
        })
    
    # Get applications grouped by platform for current user
    cur.execute("""
        SELECT p.name as platform_name, COUNT(a.id) as count
        FROM platforms p
        LEFT JOIN applications a ON a.platform_id = p.id AND a.user_id = %s
        GROUP BY p.name
        HAVING COUNT(a.id) > 0
        ORDER BY count DESC
    """, (user_id,))
    applications_by_platform = cur.fetchall()
    
    # Get applications grouped by work mode for current user
    cur.execute("""
        SELECT mode, COUNT(*) as count
        FROM applications
        WHERE user_id = %s
        GROUP BY mode
    """, (user_id,))
    applications_by_mode = cur.fetchall()
    
    # Get daily applications for the last month for current user
    cur.execute("""
        SELECT 
            application_date,
            COUNT(*) as count
        FROM applications
        WHERE application_date >= CURRENT_DATE - INTERVAL '1 month' 
        AND user_id = %s
        GROUP BY application_date
        ORDER BY application_date
    """, (user_id,))
    monthly_applications = cur.fetchall()
    
    # Get success metrics for current user
    cur.execute("SELECT COUNT(*) as offers FROM applications WHERE last_step = 6 AND user_id = %s", (user_id,))
    total_offers = cur.fetchone()['offers']
    
    cur.execute("SELECT COUNT(*) as denials FROM applications WHERE last_step = 7 AND user_id = %s", (user_id,))
    total_denials = cur.fetchone()['denials']
    
    success_rate = (
        round((total_offers / total_applications * 100), 1) 
        if total_applications > 0 else 0
    )

    # Calculate average days from application to each step for current user
    cur.execute("""
        SELECT 
            sd.name as step_name,
            sd.color as step_color,
            COALESCE(savg.avg_days, 0) as avg_days
        FROM steps_definition sd 
        LEFT JOIN (
            SELECT 
                s.step_id, 
                AVG(s.step_date - a.application_date) as avg_days
            FROM steps s
            LEFT JOIN applications a ON a.id = s.application_id
            WHERE s.step_id != 1 AND a.user_id = %s
            GROUP BY s.step_id
        ) as savg ON sd.id = savg.step_id
        ORDER BY sd.id
    """, (user_id,))
    average_days_per_step = cur.fetchall()
    
    con.close()
    
    return render_template(
        'home.html',
        total_applications=total_applications,
        conversion_data=conversion_data,
        applications_by_platform=applications_by_platform,
        applications_by_mode=applications_by_mode,
        monthly_applications=monthly_applications,
        average_days_per_step=average_days_per_step,
        total_offers=total_offers,
        total_denials=total_denials,
        success_rate=success_rate
    )

@app.route('/applications', methods=['GET', 'POST'])
@login_required
def applications():
    """
    Handle job applications listing and creation for current user.
    """
    user_id = session.get('user_id')
    
    if request.method == "GET":
        con = get_database_connection()
        cur = con.cursor()

        # Get all applications for current user
        cur.execute("""
            SELECT 
                applications.*, 
                platforms.name as platform_name, 
                steps_definition.name as step_name, 
                steps_definition.color as step_color, 
                feedbacks_definition.name as feedback_name, 
                feedbacks_definition.color as feedback_color 
            FROM applications 
            LEFT JOIN platforms ON applications.platform_id = platforms.id 
            LEFT JOIN steps_definition ON applications.last_step = steps_definition.id 
            LEFT JOIN feedbacks_definition ON applications.feedback_id = feedbacks_definition.id 
            WHERE applications.user_id = %s
            ORDER BY applications.application_date DESC
        """, (user_id,))
        applications = cur.fetchall()

        # Get reference data
        cur.execute("SELECT * FROM platforms")
        platforms = cur.fetchall()

        cur.execute("SELECT * FROM steps_definition")
        steps_definition = cur.fetchall()

        cur.execute("SELECT * FROM feedbacks_definition")
        feedbacks_definition = cur.fetchall()

        # Enhance applications with their complete step history
        applications_with_steps = []
        for app in applications:
            cur.execute("""
                SELECT 
                    s.*, 
                    sd.name as step_name, 
                    sd.description as step_description, 
                    sd.color as step_color
                FROM steps s
                JOIN steps_definition sd ON s.step_id = sd.id
                WHERE s.application_id = %s
                ORDER BY s.step_date ASC
            """, (app['id'],))
            
            steps = cur.fetchall()
            app_dict = dict(app)
            app_dict['steps'] = steps
            applications_with_steps.append(app_dict)

        con.close()
        
        return render_template(
            'applications.html', 
            applications=applications_with_steps, 
            platforms=platforms, 
            steps_definition=steps_definition, 
            feedbacks_definition=feedbacks_definition
        )
    
    if request.method == "POST":
        company = request.form.get('company')
        role = request.form.get('role')
        application_date = request.form.get('application_date')
        platform_id = request.form.get('platform_id')
        expected_salary = request.form.get('expected_salary')
        mode = request.form.get('mode')
        salary_range_min = request.form.get('salary_range_min')
        salary_range_max = request.form.get('salary_range_max')
        observation = request.form.get('observation')

        # Validação básica
        if not all([company, role, application_date, platform_id]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('applications'))

        con = get_database_connection()
        cur = con.cursor()

        try:
            # Convert empty strings to None for optional numeric fields
            expected_salary = float(expected_salary) if expected_salary and expected_salary.strip() else None
            salary_range_min = float(salary_range_min) if salary_range_min and salary_range_min.strip() else None
            salary_range_max = float(salary_range_max) if salary_range_max and salary_range_max.strip() else None
            platform_id = int(platform_id)
            
            # Insert new application for current user
            cur.execute("""
                INSERT INTO applications 
                (user_id, company, role, application_date, platform_id, expected_salary, mode, 
                 salary_range_min, salary_range_max, observation, last_step, 
                 last_step_date, feedback_id, feedback_date) 
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                user_id, company, role, application_date, platform_id, expected_salary, mode,
                salary_range_min, salary_range_max, observation, 1, application_date, 
                1, application_date
            ))
            
            result = cur.fetchone()
            if result:
                application_id = result['id']
                
                # Create the initial step record
                cur.execute("""
                    INSERT INTO steps (application_id, step_id, step_date) 
                    VALUES(%s, %s, %s)
                """, (application_id, 1, application_date))
                
                con.commit()
                flash('Application added successfully!', 'success')
            else:
                con.rollback()
                flash('Failed to create application.', 'error')
            
        except ValueError as e:
            con.rollback()
            flash('Invalid data format. Please check numeric fields.', 'error')
            print(f"ValueError: {e}")
            
        except psycopg2.IntegrityError as e:
            con.rollback()
            flash('Data integrity error. Please check if platform exists.', 'error')
            print(f"IntegrityError: {e}")
            
        except psycopg2.Error as e:
            con.rollback()
            flash('Database error occurred.', 'error')
            print(f"Database error: {e}")
            
        except Exception as e:
            con.rollback()
            flash('An unexpected error occurred.', 'error')
            print(f"Unexpected error: {e}")
            
        finally:
            con.close()
        
        return redirect(url_for('applications'))

@app.route('/applications/<int:application_id>/delete', methods=['POST'])
@login_required
def delete_application(application_id):
    """
    Delete a specific job application (only if owned by current user).
    """
    user_id = session.get('user_id')
    
    con = get_database_connection()
    cur = con.cursor()

    try:
        # Verify ownership and delete
        cur.execute("DELETE FROM applications WHERE id = %s AND user_id = %s", (application_id, user_id))
        
        if cur.rowcount > 0:
            con.commit()
            flash('Application deleted successfully!', 'success')
        else:
            flash('Application not found or access denied.', 'error')
    except Exception as e:
        con.rollback()
        flash('Failed to delete application.', 'error')
    finally:
        con.close()
    
    return redirect(url_for('applications'))

@app.route('/applications/<int:application_id>/update', methods=['POST'])
@login_required
def update_application(application_id):
    """
    Update an existing job application (only if owned by current user).
    """
    user_id = session.get('user_id')
    
    application_date = request.form.get('application_date')
    company = request.form.get('company')
    role = request.form.get('role')
    platform_id = request.form.get('platform_id')
    salary_range_min = request.form.get('salary_range_min')
    salary_range_max = request.form.get('salary_range_max')
    expected_salary = request.form.get('expected_salary')
    mode = request.form.get('mode')
    observation = request.form.get('observation')

    con = get_database_connection()
    cur = con.cursor()

    try:
        # Verify ownership and update
        cur.execute("""
            UPDATE applications 
            SET application_date = %s, company = %s, role = %s, platform_id = %s, 
                salary_range_min = %s, salary_range_max = %s, expected_salary = %s, 
                mode = %s, observation = %s 
            WHERE id = %s AND user_id = %s
        """, (
            application_date, company, role, platform_id, salary_range_min, 
            salary_range_max, expected_salary, mode, observation, application_id, user_id
        ))
        
        if cur.rowcount > 0:
            con.commit()
            flash('Application updated successfully!', 'success')
        else:
            flash('Application not found or access denied.', 'error')
    except Exception as e:
        con.rollback()
        flash('Failed to update application.', 'error')
    finally:
        con.close()
    
    return redirect(url_for('applications'))

@app.route('/applications/<int:application_id>/add-step', methods=['POST'])
@login_required
def add_step_application(application_id):
    """
    Add a new step to an existing job application (only if owned by current user).
    """
    user_id = session.get('user_id')
    step_id = request.form.get('step_id')
    step_date = request.form.get('step_date')
    observation = request.form.get('observation')
    
    con = get_database_connection()
    cur = con.cursor()

    try:
        # Verify ownership first
        cur.execute("SELECT id FROM applications WHERE id = %s AND user_id = %s", (application_id, user_id))
        if not cur.fetchone():
            flash('Application not found or access denied.', 'error')
            return redirect(url_for('applications'))

        # Insert new step record
        cur.execute("""
            INSERT INTO steps (application_id, step_id, observation, step_date) 
            VALUES (%s, %s, %s, %s)
        """, (application_id, step_id, observation, step_date))
        
        # Update application's last step information
        cur.execute("""
            UPDATE applications 
            SET last_step = %s, last_step_date = %s 
            WHERE id = %s AND user_id = %s
        """, (step_id, step_date, application_id, user_id))
        
        con.commit()
        flash("Step added successfully!", 'success')
    except Exception as e:
        con.rollback()
        flash('Failed to add step.', 'error')
    finally:
        con.close()
    
    return redirect(url_for('applications'))

@app.route('/applications/<int:application_id>/finalize', methods=['POST'])
@login_required
def finalize_application(application_id):
    """
    Finalize a job application with final outcome (only if owned by current user).
    """
    user_id = session.get('user_id')
    final_step = request.form.get('final_step')
    feedback_id = request.form.get('feedback_id')
    finalize_date = request.form.get('finalize_date')
    salary_offer = request.form.get('salary_offer')
    final_observation = request.form.get('final_observation')
    
    con = get_database_connection()
    cur = con.cursor()

    try:
        # Verify ownership first
        cur.execute("SELECT id FROM applications WHERE id = %s AND user_id = %s", (application_id, user_id))
        if not cur.fetchone():
            flash('Application not found or access denied.', 'error')
            return redirect(url_for('applications'))

        # Insert final step record
        cur.execute("""
            INSERT INTO steps (application_id, step_id, observation, step_date) 
            VALUES (%s, %s, %s, %s)
        """, (application_id, final_step, final_observation, finalize_date))
        
        # Build dynamic update query for application
        update_query = """
            UPDATE applications 
            SET last_step = %s, last_step_date = %s, feedback_id = %s, feedback_date = %s
        """
        params = [final_step, finalize_date, feedback_id, finalize_date]
        
        if salary_offer:
            update_query += ", salary_offer = %s"
            params.append(salary_offer)
        
        update_query += " WHERE id = %s AND user_id = %s"
        params.extend([application_id, user_id])
        
        cur.execute(update_query, params)
        
        con.commit()
        flash("Application finalized successfully!", 'success')
    except Exception as e:
        con.rollback()
        flash('Failed to finalize application.', 'error')
    finally:
        con.close()
    
    return redirect(url_for('applications'))

@app.route('/applications/<int:application_id>/steps/<int:step_id>/delete', methods=['POST'])
@login_required
def delete_step_application(application_id, step_id):
    """
    Delete a specific step from a job application (only if owned by current user).
    """
    user_id = session.get('user_id')
    
    con = get_database_connection()
    cur = con.cursor()

    try:
        # Verify ownership and delete step
        cur.execute("""
            DELETE FROM steps 
            WHERE application_id = %s AND id = %s 
            AND application_id IN (SELECT id FROM applications WHERE user_id = %s)
        """, (application_id, step_id, user_id))
        
        if cur.rowcount > 0:
            con.commit()
            flash('Step deleted successfully!', 'success')
        else:
            flash('Step not found or access denied.', 'error')
    except Exception as e:
        con.rollback()
        flash('Failed to delete step.', 'error')
    finally:
        con.close()
    
    return redirect(url_for('applications'))

@app.route('/applications/<int:application_id>/steps/<int:step_id>/update', methods=['POST'])
@login_required
def update_step_application(application_id, step_id):
    """
    Update a specific step in a job application (only if owned by current user).
    """
    user_id = session.get('user_id')
    steps_id = request.form.get('step_id')
    step_date = request.form.get('step_date')
    observation = request.form.get('observation')

    con = get_database_connection()
    cur = con.cursor()

    try:
        # Verify ownership and update step
        cur.execute("""
            UPDATE steps 
            SET step_id = %s, step_date = %s, observation = %s 
            WHERE application_id = %s AND id = %s 
            AND application_id IN (SELECT id FROM applications WHERE user_id = %s)
        """, (steps_id, step_date, observation, application_id, step_id, user_id))
        
        if cur.rowcount > 0:
            con.commit()
            flash('Step updated successfully!', 'success')
        else:
            flash('Step not found or access denied.', 'error')
    except Exception as e:
        con.rollback()
        flash('Failed to update step.', 'error')
    finally:
        con.close()
    
    return redirect(url_for('applications'))

# Platform routes remain mostly the same but can be accessed by any logged-in user
@app.route('/platforms', methods=['GET', 'POST'])
@login_required
def platforms():
    """
    Handle job platforms listing and creation.
    """
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

        try:
            cur.execute("INSERT INTO platforms (name, url) VALUES(%s, %s)", (name, url))
            con.commit()
            flash('Platform added successfully!', 'success')
        except Exception as e:
            con.rollback()
            flash('Failed to add platform.', 'error')
        finally:
            con.close()
        
        return redirect(url_for('platforms'))

@app.route('/platforms/<int:platform_id>/check_applications', methods=['GET'])
@login_required
def check_platform_applications(platform_id):
    """
    Check how many applications are associated with a platform.
    """
    con = get_database_connection()
    cur = con.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM applications WHERE platform_id = %s", (platform_id,))
    count = cur.fetchone()['count']
    
    con.close()
    
    return {'count': count}

@app.route('/platforms/<int:platform_id>/update', methods=['POST'])
@login_required
def update_platform(platform_id):
    """
    Update an existing platform's information.
    """
    name = request.form.get('platform_name')
    url = request.form.get('platform_url')

    con = get_database_connection()
    cur = con.cursor()

    try:
        cur.execute("""
            UPDATE platforms 
            SET name = %s, url = %s 
            WHERE id = %s
        """, (name, url, platform_id))
        
        con.commit()
        flash('Platform updated successfully!', 'success')
    except Exception as e:
        con.rollback()
        flash('Failed to update platform.', 'error')
    finally:
        con.close()
    
    return redirect(url_for('platforms'))

@app.route('/platforms/<int:platform_id>/delete', methods=['POST'])
@login_required
def delete_platform(platform_id):
    """
    Delete a platform and all associated applications.
    """
    con = get_database_connection()
    cur = con.cursor()

    try:
        # Delete all applications using this platform first
        cur.execute("DELETE FROM applications WHERE platform_id = %s", (platform_id,))
        
        # Then delete the platform itself
        cur.execute("DELETE FROM platforms WHERE id = %s", (platform_id,))
        
        con.commit()
        flash('Platform deleted successfully!', 'success')
    except Exception as e:
        con.rollback()
        flash('Failed to delete platform.', 'error')
    finally:
        con.close()
    
    return redirect(url_for('platforms'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
    Handle application settings for steps and feedback definitions.
    """
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
        
        con = get_database_connection()
        cur = con.cursor()
        
        try:
            if form_type == 'create_step_defition':
                name = request.form.get('step_name')
                description = request.form.get('step_description')
                color = request.form.get('step_color')

                cur.execute("""
                    INSERT INTO steps_definition (name, description, color) 
                    VALUES(%s, %s, %s)
                """, (name, description, color))
                
                flash('Step definition added successfully!', 'success')

            elif form_type == 'create_feedback_defition':
                name = request.form.get('feedback_name')
                description = request.form.get('feedback_description')
                color = request.form.get('feedback_color')

                cur.execute("""
                    INSERT INTO feedbacks_definition (name, description, color) 
                    VALUES(%s, %s, %s)
                """, (name, description, color))
                
                flash('Feedback definition added successfully!', 'success')
            
            con.commit()
        except Exception as e:
            con.rollback()
            flash('Failed to add definition.', 'error')
        finally:
            con.close()
            
        return redirect(url_for('settings'))

# Settings routes for steps and feedbacks remain similar but with PostgreSQL syntax
@app.route('/settings/steps/<int:step_id>/check_applications', methods=['GET'])
@login_required
def check_steps_applications(step_id):
    """
    Check how many applications are using a specific step definition.
    """
    con = get_database_connection()
    cur = con.cursor()
    
    cur.execute("""
        SELECT COUNT(DISTINCT application_id) as count
        FROM steps 
        WHERE step_id = %s
    """, (step_id,))
    count = cur.fetchone()['count']
    
    con.close()
    
    return {'count': count}

@app.route('/settings/steps/<int:step_id>/update', methods=['POST'])
@login_required
def update_step_definition(step_id):
    """
    Update an existing step definition.
    """
    name = request.form.get('step_name')
    description = request.form.get('step_description')
    color = request.form.get('step_color')

    con = get_database_connection()
    cur = con.cursor()

    try:
        cur.execute("""
            UPDATE steps_definition 
            SET name = %s, description = %s, color = %s 
            WHERE id = %s
        """, (name, description, color, step_id))
        
        con.commit()
        flash('Step definition updated successfully!', 'success')
    except Exception as e:
        con.rollback()
        flash('Failed to update step definition.', 'error')
    finally:
        con.close()
    
    return redirect(url_for('settings'))

@app.route('/settings/steps/<int:step_id>/delete', methods=['POST'])
@login_required
def delete_step_definition(step_id):
    """
    Delete a step definition and all applications that use it.
    """
    con = get_database_connection()
    cur = con.cursor()

    try:
        # Delete all applications that have used this step
        cur.execute("""
            DELETE FROM applications 
            WHERE id IN (
                SELECT application_id 
                FROM steps 
                WHERE step_id = %s
            )
        """, (step_id,))
        
        # Delete the step definition
        cur.execute("DELETE FROM steps_definition WHERE id = %s", (step_id,))
        
        con.commit()
        flash('Step definition deleted successfully!', 'success')
    except Exception as e:
        con.rollback()
        flash('Failed to delete step definition.', 'error')
    finally:
        con.close()
    
    return redirect(url_for('settings'))

@app.route('/settings/feedbacks/<int:feedback_id>/check_applications', methods=['GET'])
@login_required
def check_feedbacks_applications(feedback_id):
    """
    Check how many applications are using a specific feedback definition.
    """
    con = get_database_connection()
    cur = con.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM applications WHERE feedback_id = %s", (feedback_id,))
    count = cur.fetchone()['count']
    
    con.close()
    
    return {'count': count}

@app.route('/settings/feedbacks/<int:feedback_id>/update', methods=['POST'])
@login_required
def update_feedback_definition(feedback_id):
    """
    Update an existing feedback definition.
    """
    name = request.form.get('feedback_name')
    description = request.form.get('feedback_description')
    color = request.form.get('feedback_color')

    con = get_database_connection()
    cur = con.cursor()

    try:
        cur.execute("""
            UPDATE feedbacks_definition 
            SET name = %s, description = %s, color = %s 
            WHERE id = %s
        """, (name, description, color, feedback_id))
        
        con.commit()
        flash('Feedback definition updated successfully!', 'success')
    except Exception as e:
        con.rollback()
        flash('Failed to update feedback definition.', 'error')
    finally:
        con.close()
    
    return redirect(url_for('settings'))

@app.route('/settings/feedbacks/<int:feedback_id>/delete', methods=['POST'])
@login_required
def delete_feedback_definition(feedback_id):
    """
    Delete a feedback definition and all applications that use it.
    """
    con = get_database_connection()
    cur = con.cursor()

    try:
        # Delete all applications using this feedback
        cur.execute("DELETE FROM applications WHERE feedback_id = %s", (feedback_id,))
        
        # Delete the feedback definition
        cur.execute("DELETE FROM feedbacks_definition WHERE id = %s", (feedback_id,))
        
        con.commit()
        flash('Feedback definition deleted successfully!', 'success')
    except Exception as e:
        con.rollback()
        flash('Failed to delete feedback definition.', 'error')
    finally:
        con.close()
    
    return redirect(url_for('settings'))

@app.route('/profile')
@login_required
def profile():
    """
    Display user profile information.
    """
    user_id = session.get('user_id')
    
    con = get_database_connection()
    cur = con.cursor()
    
    try:
        cur.execute("""
            SELECT username, email, first_name, last_name, current_company, 
                   current_salary, experience_years, tech_stack, created_at
            FROM users 
            WHERE id = %s
        """, (user_id,))
        
        user = cur.fetchone()
        
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('logout'))
            
        return render_template('profile.html', user=user)
        
    except Exception as e:
        flash('Failed to load profile.', 'error')
        return redirect(url_for('home'))
    finally:
        con.close()

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """
    Update user profile information.
    """
    user_id = session.get('user_id')
    
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    current_company = request.form.get('current_company')
    current_salary = request.form.get('current_salary')
    experience_years = request.form.get('experience_years')
    tech_stack = request.form.get('tech_stack')
    
    con = get_database_connection()
    cur = con.cursor()
    
    try:
        # Check if email is already used by another user
        cur.execute("SELECT id FROM users WHERE email = %s AND id != %s", (email, user_id))
        if cur.fetchone():
            flash('Email is already in use by another account.', 'error')
            return redirect(url_for('profile'))
        
        # Update user information
        cur.execute("""
            UPDATE users 
            SET first_name = %s, last_name = %s, email = %s, current_company = %s,
                current_salary = %s, experience_years = %s, tech_stack = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (first_name, last_name, email, current_company, current_salary, 
              experience_years, tech_stack, user_id))
        
        con.commit()
        
        # Update session data
        session['email'] = email
        session['first_name'] = first_name
        session['last_name'] = last_name
        
        flash('Profile updated successfully!', 'success')
        
    except Exception as e:
        con.rollback()
        flash('Failed to update profile.', 'error')
    finally:
        con.close()
    
    return redirect(url_for('profile'))

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """
    Change user password.
    """
    user_id = session.get('user_id')
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Basic validation
    if not all([current_password, new_password, confirm_password]):
        flash('Please fill in all password fields.', 'error')
        return redirect(url_for('profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match.', 'error')
        return redirect(url_for('profile'))
    
    if len(new_password) < 6:
        flash('New password must be at least 6 characters long.', 'error')
        return redirect(url_for('profile'))
    
    con = get_database_connection()
    cur = con.cursor()
    
    try:
        # Verify current password
        hashed_current = hash_password(current_password)
        cur.execute("SELECT id FROM users WHERE id = %s AND password_hash = %s", 
                   (user_id, hashed_current))
        
        if not cur.fetchone():
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('profile'))
        
        # Update password
        hashed_new = hash_password(new_password)
        cur.execute("""
            UPDATE users 
            SET password_hash = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (hashed_new, user_id))
        
        con.commit()
        flash('Password changed successfully!', 'success')
        
    except Exception as e:
        con.rollback()
        flash('Failed to change password.', 'error')
    finally:
        con.close()
    
    return redirect(url_for('profile'))


# Application entry point
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8088)