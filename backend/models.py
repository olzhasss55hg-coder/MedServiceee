import uuid
import datetime
from sqlalchemy import Boolean, Column, String, Float, DateTime, Enum as SQLAlchemyEnum, Numeric, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from database import Base

class CategoryEnum(str, enum.Enum):
    laboratory = "лаборатория"
    doctor_appointment = "приём врача"
    diagnostics = "диагностика"
    procedure = "процедура"

class CurrencyEnum(str, enum.Enum):
    KZT = "KZT"
    USD = "USD"

class Clinic(Base):
    __tablename__ = "clinics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, index=True)
    city = Column(String, index=True)
    address = Column(String)
    phone = Column(String, nullable=True)
    working_hours = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)

    prices = relationship("Price", back_populates="clinic")
    subscriptions = relationship("UserSubscription", back_populates="clinic")
    doctors = relationship("Doctor", back_populates="clinic")

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    clinic_id = Column(String, ForeignKey("clinics.id"), index=True)
    first_name = Column(String)
    last_name = Column(String)
    specialty = Column(String)
    experience_years = Column(Integer)
    rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)
    consultation_price = Column(Numeric(10, 2))
    photo_url = Column(String, nullable=True)
    description = Column(String, nullable=True)

    clinic = relationship("Clinic", back_populates="doctors")

class Service(Base):
    __tablename__ = "services"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name_raw = Column(String, index=True)
    name_norm = Column(String, index=True, nullable=True)
    category = Column(SQLAlchemyEnum(CategoryEnum), index=True)

    prices = relationship("Price", back_populates="service")
    subscriptions = relationship("UserSubscription", back_populates="service")

class Price(Base):
    __tablename__ = "prices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    clinic_id = Column(String, ForeignKey("clinics.id"))
    service_id = Column(String, ForeignKey("services.id"))
    
    price_kzt = Column(Numeric(10, 2))
    currency = Column(SQLAlchemyEnum(CurrencyEnum), default=CurrencyEnum.KZT)
    duration_days = Column(Integer, nullable=True)
    parsed_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)

    clinic = relationship("Clinic", back_populates="prices")
    service = relationship("Service", back_populates="prices")
    history = relationship("PriceHistory", back_populates="price_parent")

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    price_id = Column(String, ForeignKey("prices.id"))
    old_price_kzt = Column(Numeric(10, 2), nullable=True)
    new_price_kzt = Column(Numeric(10, 2))
    changed_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    price_parent = relationship("Price", back_populates="history")

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    subscriptions = relationship("UserSubscription", back_populates="user")

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, ForeignKey("users.id"))
    service_id = Column(String, ForeignKey("services.id"))
    clinic_id = Column(String, ForeignKey("clinics.id"), nullable=True) # Optional, can subscribe to any clinic for this service
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="subscriptions")
    service = relationship("Service", back_populates="subscriptions")
    clinic = relationship("Clinic", back_populates="subscriptions")
