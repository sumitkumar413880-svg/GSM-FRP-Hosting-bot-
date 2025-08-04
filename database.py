from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import DATABASE_URL

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)  # Telegram user ID
    username = Column(String(50))
    email = Column(String(100))
    password_hash = Column(String(255))
    balance = Column(Float, default=0.0)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = relationship("Order", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

class Service(Base):
    __tablename__ = 'services'
    
    service_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)  # Price in credits
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = relationship("Order", back_populates="service")

class Order(Base):
    __tablename__ = 'orders'
    
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.service_id'), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='pending')  # pending, processing, completed, failed
    device_info = Column(Text)  # JSON string with device details
    fulfillment_details = Column(Text)  # JSON string with fulfillment info
    
    # Relationships
    user = relationship("User", back_populates="orders")
    service = relationship("Service", back_populates="orders")

class Transaction(Base):
    __tablename__ = 'transactions'
    
    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    amount = Column(Float, nullable=False)  # Credits
    transaction_type = Column(String(20), nullable=False)  # credit_purchase, service_purchase
    date = Column(DateTime, default=datetime.utcnow)
    payment_gateway_ref = Column(String(100))
    
    # Relationships
    user = relationship("User", back_populates="transactions")

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

