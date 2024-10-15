from flask import Flask, render_template, request, redirect, url_for
from models.models import db, UserSubmission
import os

app = Flask(__name__)

# Set the path for the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///submissions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with Flask
db.init_app(app)

# Create the database tables
with app.app_context():
    db.create_all()

# Ensure that the "uploads" directory exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Route to render the multistep form
@app.route('/')
def index():
    return render_template('index.html')
    
# Handle form submission and save data to the database
@app.route('/submit', methods=['POST'])
def submit_form():
    name = request.form['name']
    email = request.form['email']
    
    # Get the captured image and signature from the form
    identity_image = request.form.get('identity_image')  # base64 string for captured image
    signature = request.form.get('signature')  # base64 string for signature

    # Save uploaded documents
    documents = request.files.getlist("documents[]")
    document_paths = []
    for document in documents:
        if document.filename != '':  # Only save if a file was actually uploaded
            file_path = os.path.join(UPLOAD_FOLDER, document.filename)
            document.save(file_path)
            document_paths.append(file_path)

    # Save form data into the database
    new_submission = UserSubmission(
        name=name,
        email=email,
        documents=";".join(document_paths),  # Store document paths in the database
        identity_image=identity_image,  # Store base64 image string
        signature=signature  # Store base64 signature string
    )
    db.session.add(new_submission)
    db.session.commit()

    # Redirect to the Thank You page after submission
    return redirect(url_for('thank_you'))

# Thank you page
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    # Fetch all submissions from the database
    submissions = UserSubmission.query.all()

    return render_template('dashboard.html', submissions=submissions)

# Route to delete a submission
@app.route('/delete/<int:id>', methods=['POST'])
def delete_submission(id):
    # Find the submission by ID
    submission = UserSubmission.query.get(id)
    
    if submission:
        # Delete the record
        db.session.delete(submission)
        db.session.commit()
    
    # Redirect back to the dashboard after deletion
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
