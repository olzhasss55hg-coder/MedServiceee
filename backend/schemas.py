from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum

class CategoryEnum(str, Enum):
    laboratory = "лаборатория"
    doctor_appointment = "приём врача"
    diagnostics = "диагностика"
    procedure = "процедура"

class CurrencyEnum(str, Enum):
    KZT = "KZT"
    USD = "USD"

# Clinic Schemas
class ClinicBase(BaseModel):
    name: str
    city: str
    address: str
    phone: Optional[str] = None
    working_hours: Optional[str] = None
    source_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating: Optional[float] = 0.0
    reviews_count: Optional[int] = 0

class ClinicCreate(ClinicBase):
    pass

class Clinic(ClinicBase):
    id: str

    model_config = ConfigDict(from_attributes=True)

# Doctor Schemas
class DoctorBase(BaseModel):
    clinic_id: str
    first_name: str
    last_name: str
    specialty: str
    experience_years: int
    rating: float = 0.0
    reviews_count: int = 0
    consultation_price: float
    photo_url: Optional[str] = None
    description: Optional[str] = None

class DoctorCreate(DoctorBase):
    pass

class Doctor(DoctorBase):
    id: str

    model_config = ConfigDict(from_attributes=True)

# Service Schemas
class ServiceBase(BaseModel):
    name_raw: str
    name_norm: Optional[str] = None
    category: CategoryEnum

class ServiceCreate(ServiceBase):
    pass

class Service(ServiceBase):
    id: str

    model_config = ConfigDict(from_attributes=True)

# Price History Schemas
class PriceHistory(BaseModel):
    id: str
    price_id: str
    old_price_kzt: Optional[float] = None
    new_price_kzt: float
    changed_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Price Schemas
class PriceBase(BaseModel):
    clinic_id: str
    service_id: str
    price_kzt: float
    currency: CurrencyEnum = CurrencyEnum.KZT
    duration_days: Optional[int] = None
    parsed_at: Optional[datetime] = None
    is_active: bool = True

class PriceCreate(PriceBase):
    pass

class Price(PriceBase):
    id: str
    parsed_at: datetime
    clinic: Clinic
    service: Service
    history: List[PriceHistory] = []

    model_config = ConfigDict(from_attributes=True)

# Unified Search Result Schema
class UnifiedSearchResult(BaseModel):
    service: Service
    avg_price: float
    min_price: float
    clinics_count: int
    best_offer_clinic: Optional[Clinic] = None
    best_offer_price: Optional[float] = None
    last_updated_at: Optional[datetime] = None

# User & Auth Schemas
class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Subscription Schemas
class SubscriptionCreate(BaseModel):
    service_id: str
    clinic_id: Optional[str] = None

class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    service_id: str
    clinic_id: Optional[str] = None
    created_at: datetime
    service: Service
    clinic: Optional[Clinic] = None
    
    model_config = ConfigDict(from_attributes=True)

class ClinicDetailResponse(BaseModel):
    clinic: Clinic
    services: List[Price]
    doctors: List[Doctor] = []
    
    model_config = ConfigDict(from_attributes=True)
