from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import sessionmaker
from base import Base  # Ensure this imports from your base class (declarative_base)

class FormSubmission(Base):
    __tablename__ = 'form_submissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    id_number = Column(String(20), nullable=False)
    phone_number = Column(String(15), nullable=False)
    kra_pin = Column(String(20), nullable=False)
    address = Column(String(255), nullable=True)
    code = Column(String(20), nullable=True)
    town = Column(String(100), nullable=True)
    email_address = Column(String(100), nullable=False)
    personal_relief = Column(Boolean, nullable=False)
    data_protection_accepted = Column(Boolean, nullable=False)
    signature_data = Column(String, nullable=True)  # Store base64 encoded signature image, if applicable
    photo_data = Column(String, nullable=True)  # Store base64 encoded photo image, if applicable
    created_at = Column(DateTime, default=datetime.utcnow)

    # File upload columns (store paths to uploaded files)
    id_card_front = Column(String(255), nullable=True)
    id_card_back = Column(String(255), nullable=True)
    kra_pin_certificate = Column(String(255), nullable=True)
    atm_card = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<FormSubmission(id={self.id}, full_name={self.full_name})>"



class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(80), nullable=False)
    lastname = Column(String(80), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    newsletter = Column(Boolean, default=False)
    access_level = Column(String(20), nullable=True)  # Access level can be NULL
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    def set_password(self, password):
        """Hashes the password for storage."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks the password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User(email={self.email})>"


# Optional: Create a LoginAttempt model for tracking
class LoginAttempt(Base):
    __tablename__ = 'login_attempts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    email = Column(String(120), nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(256), nullable=True)
    success = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)