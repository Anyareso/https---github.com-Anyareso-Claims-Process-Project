import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from models import FormSubmission
from base import Base  # Import the base class from your base file

import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Database setup for SQL Server
SERVER = 'localhost\\SQLEXPRESS'  # Use localhost or IP address
DATABASE = 'vc_test'
DRIVER = 'ODBC Driver 18 for SQL Server'

# Use this format for SQLAlchemy with pyodbc
DATABASE_URI = 'mssql+pyodbc://localhost\\SQLEXPRESS/vc_test?driver=ODBC+Driver+18+for+SQL+Server&Trusted_Connection=yes&Encrypt=no&TrustServerCertificate=yes'

# Set up the engine and session
engine = create_engine(DATABASE_URI)
print("Engine created successfully!")
Session = sessionmaker(bind=engine)
session = Session()

# Create the table(s) if they do not exist
try:
    Base.metadata.create_all(engine)
    print("Tables created successfully!")
except SQLAlchemyError as e:
    print(f"Error occurred while creating tables: {e}")

# Configure the upload folder for file storage allowed file extensions
app.config['UPLOAD_FOLDER'] = 'uploads'
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
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    return None

@app.route('/')
def main_page():
    return render_template('vc.html')  # Serves the main page (vc.html)

@app.route('/thank-you')
def thank_you_page():
    return render_template('thank_you.html')  # Serves the thank-you page

@app.route('/submit-form', methods=['POST'])
def submit_form():
    try:
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
        photo_data = request.form['photoData']
        signature_data = request.form['signatureData']

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
            photo_data=photo_data,
            signature_data=signature_data,
            id_card_front=id_card_front,
            id_card_back=id_card_back,
            kra_pin_certificate=kra_pin_certificate,
            atm_card=atm_card
        )

        # Save the form submission to the database
        session.add(form_submission)
        session.commit()
        
        # Redirect to the thank-you page
        return redirect(url_for('thank_you_page'))
    
    except Exception as e:
        session.rollback()
        return jsonify({"message": f"Error submitting form: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
