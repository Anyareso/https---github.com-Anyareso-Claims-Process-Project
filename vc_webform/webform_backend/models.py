from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
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
    town = Column(String(100), nullable=Trur)
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
