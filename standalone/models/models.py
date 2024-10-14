from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class UserSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    documents = db.Column(db.Text)  # store document paths
    identity_image = db.Column(db.Text, nullable=True)  # store base64 image string
    signature = db.Column(db.Text, nullable=True)  # store base64 signature string

