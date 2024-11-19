import os
import re
import base64
import secrets
import csv
import sentry_sdk
from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory, flash, send_file, session
from flask_session import Session
from flask_wtf.csrf import CSRFProtect, CSRFError
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from validate_email import validate_email  # pip install py3-validate-email
from io import BytesIO
from datetime import datetime, timedelta
from models import FormSubmission
from models import User
from base import Base  # Import the base class from your base file

import logging
logging.basicConfig(level=logging.INFO)

sentry_sdk.init(
    dsn="https://7c0e9de1b2cbed0e86d02472115b5727@o4508312518328320.ingest.de.sentry.io/4508312522260560",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    _experiments={
        # Set continuous_profiling_auto_start to True
        # to automatically start the profiler on when
        # possible.
        "continuous_profiling_auto_start": True,
    },
)

csrf = CSRFProtect(app)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generates a random 32-character secret key
# # Session timeout duration (e.g., 30 minutes)
app.config['SESSION_TYPE'] = 'filesystem'  # Or another session type like 'redis', etc.
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
flask_session = Session(app)

# Database setup for SQL Server
SERVER = 'localhost\\SQLEXPRESS'  # Use localhost or IP address
DATABASE = 'vc_test'
DRIVER = 'ODBC Driver 18 for SQL Server'

# Use this format for SQLAlchemy with pyodbc
DATABASE_URI = 'mssql+pyodbc://localhost\\SQLEXPRESS/vc_test?driver=ODBC+Driver+18+for+SQL+Server&Trusted_Connection=yes&Encrypt=no&TrustServerCertificate=yes'

# Set up the engine and session
engine = create_engine(DATABASE_URI)
# Create the session correctly
session = Session(bind=engine)

# Create the table(s) if they do not exist
try:
    Base.metadata.create_all(engine)
    print("Tables created successfully!")
except SQLAlchemyError as e:
    print(f"Error occurred while creating tables: {e}")

# Configure the upload folder for file storage allowed file extensions
app.config['UPLOAD_FOLDER'] = '/vc_webform/webform_backend/uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'docx', 'txt'}

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper function to save uploaded files
def save_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        logging.info(f"File saved to {file_path}")
        return filename
    return None

# Helper function to save base64 encoded image data
def save_base64_image(data, filename):
    # Decode the base64 image
    image_data = base64.b64decode(data.split(',')[1])  # Decode base64 data
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Save the image to the defined folder
    with open(file_path, 'wb') as f:
        f.write(image_data)
    
    logging.info(f"Image saved to {file_path}")
    
    # Save only the relative path (without 'uploads/' prefix) to the database
    relative_file_path = os.path.relpath(file_path, app.config['UPLOAD_FOLDER']).replace("\\", "/")
    return relative_file_path

@app.route('/')
def main_page():
    return render_template('vc.html')  # Serves the main page (vc.html)

@app.route('/thank-you')
def thank_you_page():
    return render_template('thank_you.html')  # Serves the thank-you page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            remember_me = data.get('rememberMe')

            # Database operations using db_session
            with Session(engine) as db_session:
                user = db_session.query(User).filter_by(email=email).first()
                
                if not user:
                    return jsonify({
                        'success': False, 
                        'message': 'Invalid email or password'
                    }), 401

                if not check_password_hash(user.password, password):
                    return jsonify({
                        'success': False, 
                        'message': 'Invalid email or password'
                    }), 401

                # Flask session management for cookies
                session['user_id'] = user.id
                session['email'] = user.email
                
                if remember_me:
                    session.permanent = True
                    # Optional: Set custom lifetime
                    # app.permanent_session_lifetime = timedelta(days=30)

                # Flash message for success
                flash('Login successful!', 'success')
                    
                return jsonify({
                    'success': True, 
                    'message': 'Login successful'
                })

        except Exception as e:
            print(f"Login error: {str(e)}")
            # Flash message for error
            flash('An error occurred during login', 'error')
            return jsonify({
                'success': False, 
                'message': 'An error occurred during login'
            }), 500

@app.route('/logout')
def logout():
    # Clear session and redirect to login page
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Extract data
            firstname = data.get('firstname', '').strip()
            lastname = data.get('lastname', '').strip()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            newsletter = data.get('newsletter', False)

            errors = {}

            # Validate firstname
            if not firstname:
                errors['firstname'] = 'First name is required'
            elif len(firstname) < 2:
                errors['firstname'] = 'First name must be at least 2 characters'
            elif len(firstname) > 80:
                errors['firstname'] = 'First name must be less than 80 characters'
            elif not re.match(r'^[a-zA-Z\s-]+$', firstname):
                errors['firstname'] = 'First name can only contain letters, spaces, and hyphens'

            # Validate lastname
            if not lastname:
                errors['lastname'] = 'Last name is required'
            elif len(lastname) < 2:
                errors['lastname'] = 'Last name must be at least 2 characters'
            elif len(lastname) > 80:
                errors['lastname'] = 'Last name must be less than 80 characters'
            elif not re.match(r'^[a-zA-Z\s-]+$', lastname):
                errors['lastname'] = 'Last name can only contain letters, spaces, and hyphens'

            # Validate email
            if not email:
                errors['email'] = 'Email is required'
            elif not validate_email(email):
                errors['email'] = 'Invalid email address'
            elif User.query.filter_by(email=email).first():
                errors['email'] = 'Email already registered'

            # Validate password
            if not password:
                errors['password'] = 'Password is required'
            elif len(password) < 8:
                errors['password'] = 'Password must be at least 8 characters'
            elif not re.search(r'[A-Z]', password):
                errors['password'] = 'Password must contain at least one uppercase letter'
            elif not re.search(r'[a-z]', password):
                errors['password'] = 'Password must contain at least one lowercase letter'
            elif not re.search(r'[0-9]', password):
                errors['password'] = 'Password must contain at least one number'
            elif not re.search(r'[^A-Za-z0-9]', password):
                errors['password'] = 'Password must contain at least one special character'

            if errors:
                return jsonify({'success': False, 'errors': errors}), 400

            # Create new user
            new_user = User(
                firstname=firstname,
                lastname=lastname,
                email=email,
                newsletter=newsletter,
                access_level='user',  # Default access level
                created_at=datetime.utcnow()
            )
            new_user.set_password(password)

            # Add to database
            db.session.add(new_user)
            db.session.commit()

            # Optional: Send welcome email
            try:
                send_welcome_email(new_user)
            except Exception as e:
                # Log the error but don't stop the registration process
                current_app.logger.error(f"Failed to send welcome email: {str(e)}")

            return jsonify({
                'success': True,
                'message': 'Registration successful!',
                'redirect': url_for('login')
            }), 201

        except IntegrityError:
            db.session.rollback()
            return jsonify({
                'success': False,
                'errors': {'email': 'Email already registered'}
            }), 400
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'An error occurred during registration'
            }), 500

# Optional: Email sending function
def send_welcome_email(user):
    """Send welcome email to newly registered user"""
    try:
        msg = Message(
            "Welcome to Our Platform!",
            recipients=[user.email]
        )
        msg.body = f"""
        Hi {user.firstname},

        Welcome to our platform! We're excited to have you on board.

        Best regards,
        Your Platform Team
        """
        mail.send(msg)
    except Exception as e:
        # Log the error but don't raise it
        current_app.logger.error(f"Email sending failed: {str(e)}")

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')  # Serves the forgot_password page

@app.route('/submit-form', methods=['POST'])
def submit_form():
    print("Reached submit_form function")
    logging.info("Form submission route accessed")  # Test log message
    try:
        with Session(engine) as db_session:
            logging.info("Getting form data...")
            logging.info("Form submission route accessed")
            
            # Log all incoming form data
            for key, value in request.form.items():
                logging.info(f"Form data - {key}: {value}")

            # Handle file data as well
            for file_key, file_value in request.files.items():
                logging.info(f"File data - {file_key}: {file_value.filename}")

            # Get form data
            full_name = request.form['fullName']
            id_number = request.form['idNumber']
            phone_number = request.form['phoneNumber']
            kra_pin = request.form['kraPin']
            address = request.form['address']
            code = request.form['code']
            town = request.form['town']
            email_address = request.form['emailAddress']
            personal_relief = request.form['personalRelief'] == 'yes'
            data_protection_accepted = request.form['dataProtectionAccepted'] == 'true'
            photo_data = request.form.get('photo')  # Get the photo data (base64 string)
            signature_data = request.form['signature']
        

            # Print out the form data to verify it's being captured correctly
            print(f"Form data: {full_name}, {id_number}, {phone_number}, {email_address}, {photo_data}, {signature_data}")

            # Save base64 photo data
            photo_filename = f"{id_number}_photo.png"
            photo_file_path = save_base64_image(photo_data, photo_filename)

            # Save base64 signature data
            signature_filename = f"{id_number}_signature.png"
            signature_file_path = save_base64_image(signature_data, signature_filename)

            # Handle file uploads
            id_card_front = save_file(request.files.get('id-card-front'))
            id_card_back = save_file(request.files.get('id-card-back'))
            kra_pin_certificate = save_file(request.files.get('kra-pin-certificate'))
            atm_card = save_file(request.files.get('atm-card'))

            # Create FormSubmission instance
            form_submission = FormSubmission(
                full_name=full_name,
                id_number=id_number,
                phone_number=phone_number,
                kra_pin=kra_pin,
                address=address,
                code=code,
                town=town,
                email_address=email_address,
                personal_relief=personal_relief,
                data_protection_accepted=data_protection_accepted,
                photo_data=photo_file_path,  # Store file path instead of base64 data
                signature_data=signature_file_path,  # Store file path instead of base64 data
                id_card_front=id_card_front,
                id_card_back=id_card_back,
                kra_pin_certificate=kra_pin_certificate,
                atm_card=atm_card
            )

            # Save the form submission to the database
            db_session.add(form_submission)
            db_session.commit()

            # Log success
            logging.info(f"Form submission for {full_name} added to the database.")

            # Return success response
            return jsonify({'success': True})
    
    except Exception as e:
        db_session.rollback()
        logging.error(f"Error submitting form: {str(e)}")
        return jsonify({"message": f"Error submitting form: {str(e)}"}), 500

# Route for the dashboard
@app.route('/dashboard')
def dashboard():
    try:
        with Session(engine) as db_session:
            # Query to fetch all submissions
            submissions = db_session.query(FormSubmission).all()
            return render_template('vc_dashboard.html', submissions=submissions)
    except Exception as e:
        return f"An error occurred: {e}"

# Route for individual submission details
@app.route('/submission/<int:submission_id>')
def submission_details(submission_id):
    try:
        with Session(engine) as db_session:
            submission = db_session.query(FormSubmission).get(submission_id)
            if not submission:
                return "Submission not found", 404
            return render_template('vc_submission_details.html', submission=submission)
    except Exception as e:
        return f"An error occurred: {e}"

# Route to serve files from the uploads directory
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Safely join the base upload folder path with the filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        abort(404)
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Route to handle the deletion logic
@app.route('/delete_submission/<int:submission_id>', methods=['POST'])
def delete_submission(submission_id):
    try:
        with Session(engine) as db_session:
            # Find the submission by ID
            submission = db_session.query(FormSubmission).get(submission_id)
            
            if submission:
                # Delete the associated files from the file system if they exist
                file_paths = [
                    submission.photo_data,
                    submission.signature_data,
                    submission.id_card_front,
                    submission.id_card_back,
                    submission.kra_pin_certificate,
                    submission.atm_card
                ]
                
                for file_path in file_paths:
                    if file_path:
                        try:
                            os.remove(file_path)  # Delete each file if it exists
                        except FileNotFoundError:
                            pass  # Handle the case where the file might not exist
                
                # Delete the submission record from the database
                db_session.delete(submission)
                db_session.commit()
                
                flash('Submission deleted successfully!', 'success')  # Flash message for confirmation
            else:
                flash('Submission not found!', 'danger')  # Flash message for error
    except Exception as e:
        flash(f"An error occurred: {e}", 'danger')  # Flash message for general errors
    
    return redirect(url_for('dashboard'))  # Redirect to dashboard after deletion

# Route to generate CSV reports
@app.route('/export_csv', methods=['GET'])
def export_csv():
    try:
        with Session(engine) as db_session:
            # Get the start and end date from the request parameters
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')

            # Convert the date strings to datetime objects
            start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
            end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

            # Validation: Ensure start_date is not later than end_date
            if start_date and end_date and start_date > end_date:
                flash('Please select both start and end dates.','danger')
                return redirect(request.referrer)  # Redirect to the same page or dashboard

            # Query the FormSubmission table with date filters
            query = db_session.query(FormSubmission)

            # Apply date filters if provided
            if start_date:
                query = query.filter(FormSubmission.created_at >= start_date)
            if end_date:
                query = query.filter(FormSubmission.created_at <= end_date)

            # Fetch the filtered submissions
            submissions = query.all()

            # If no records found, send an empty CSV with headers
            if not submissions:
                flash("No records found for the selected date range.","warning")
                # Create an empty CSV with just headers
                output = BytesIO()
                csv_writer = csv.writer(output)
                csv_writer.writerow([
                    'Policy No.', 'Name', 'ID Number', 'Phone Number', 'Email', 'KRA Pin No.',
                    'Captured Image', 'ID Photo', 'KRA Pin Photo', 'ATM Card Photo', 'Personal Relief',
                    'Signature', 'Data Protection Consent', 'Date Submitted'
                ])
                output.seek(0)
                return send_file(output, mimetype='text/csv', as_attachment=True, download_name=f'form_submissions_empty_{datetime.now().strftime("%Y%m%d%H%M%S")}.csv')

            # Create a CSV in memory using StringIO first, then convert to bytes
            from io import StringIO
            output_str = StringIO()
            csv_writer = csv.writer(output_str)
            csv_writer.writerow([
                'Policy No.', 'Name', 'ID Number', 'Phone Number', 'Email', 'KRA Pin No.',
                'Captured Image', 'ID Photo', 'KRA Pin Photo', 'ATM Card Photo', 'Personal Relief',
                'Signature', 'Data Protection Consent', 'Date Submitted'
            ])

            # Write each submission row to the CSV
            for submission in submissions:
                csv_writer.writerow([
                    submission.id_number,
                    submission.full_name,
                    submission.id_number,
                    submission.phone_number,
                    submission.email_address,
                    submission.kra_pin,
                    submission.photo_data,  # Base64 or URL of the photo
                    submission.id_card_front,
                    submission.kra_pin_certificate,
                    submission.atm_card,
                    submission.personal_relief,
                    submission.signature_data,  # Base64 or URL of the signature
                    submission.data_protection_accepted,
                    submission.created_at.strftime('%Y-%m-%d %H:%M:%S')  # Date submitted
                ])

            # Convert the StringIO content to bytes
            output_bytes = BytesIO(output_str.getvalue().encode('utf-8'))
            output_bytes.seek(0)

            # Send the CSV file as a response and add a timestamp to the filename for uniqueness
            return send_file(output_bytes, mimetype='text/csv', as_attachment=True, download_name=f'form_submissions_{datetime.now().strftime("%Y%m%d%H%M%S")}.csv')

    except Exception as e:
        # Log the error and provide a user-friendly message
        flash(f"An error occurred while exporting: {str(e)}", "error")
        return redirect(request.referrer)  # Redirect back to the page where the export was triggered

# Route to handle flash messages
@app.route('/trigger_flash_message', methods=['POST'])
def trigger_flash_message():
    try:
        # Get the JSON data from the request
        data = request.get_json()
        
        # Extract the message and category
        message = data.get('message')
        category = data.get('category')
        
        # Validate if the message and category are provided
        if not message or not category:
            return jsonify({"error": "Both message and category are required"}), 400
        
        # Flash the message with the appropriate category
        flash(message,category)
        
        return jsonify({"status": "success"}), 200  # Respond with success
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Handle any other errors
        
#Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'success': False,
        'message': 'Resource not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'An internal server error occurred'
    }), 500

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return jsonify({
        'success': False,
        'message': 'CSRF token verification failed'
    }), 400


if __name__ == '__main__':
    app.run(debug=True)
