"""MedServicePrice API — Main application entry point."""

from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import os
from contextlib import asynccontextmanager
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from jose import JWTError, jwt

import models, schemas, auth
from database import engine, get_db
import meilisearch
from scheduler_tasks import start_scheduler, stop_scheduler
import chat_ai
from pydantic import BaseModel
from logger import api_logger

class ChatRequest(BaseModel):
    message: str

MEILI_URL = os.getenv("MEILI_URL", "http://meilisearch:7700")
MEILI_MASTER_KEY = os.getenv("MEILI_MASTER_KEY", "masterKey123")
meili_client = meilisearch.Client(MEILI_URL, MEILI_MASTER_KEY)

# Recreate tables (drop first) to apply new schema for Full MVP (users, subscriptions, map)
models.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(title="MedServicePrice API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*", 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "MedServicePrice API is running"}

# --- Auth API ---
@app.post("/api/auth/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/auth/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# --- Search API ---
@app.get("/api/search", response_model=List[schemas.UnifiedSearchResult])
def search_services(q: str = Query(..., min_length=2), city: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        search_res = meili_client.index('services').search(q, {'limit': 20})
        hits = search_res.get('hits', [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Meilisearch error: {str(e)}")
        
    results = []
    for hit in hits:
        service_id = hit['id']
        service = db.query(models.Service).filter(models.Service.id == service_id).first()
        if not service:
            continue
            
        prices = db.query(models.Price).filter(models.Price.service_id == service_id).all()
        if city:
            prices = [p for p in prices if p.clinic.city == city]
            
        if not prices:
            continue
            
        prices_list = [p.price_kzt for p in prices if p.price_kzt]
        if not prices_list:
            continue
            
        min_price = min(prices_list)
        avg_price = sum(prices_list) / len(prices_list)
        
        best_price_obj = min(prices, key=lambda p: p.price_kzt)
        
        results.append(schemas.UnifiedSearchResult(
            service=service,
            avg_price=float(avg_price),
            min_price=float(min_price),
            clinics_count=len(prices),
            best_offer_clinic=best_price_obj.clinic,
            best_offer_price=float(best_price_obj.price_kzt),
            last_updated_at=best_price_obj.parsed_at
        ))
        
    return results

@app.post("/api/chat")
def chat_with_ai(req: ChatRequest, db: Session = Depends(get_db)):
    """Process a user message through the AI chat assistant."""
    try:
        reply = chat_ai.generate_ai_response(req.message, db)
        return {"reply": reply}
    except Exception as e:
        api_logger.error("Chat API Error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="AI Error")

# --- Clinics & Services API ---
@app.get("/api/clinics", response_model=List[schemas.Clinic])
def read_clinics(city: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(models.Clinic)
    if city:
        query = query.filter(models.Clinic.city == city)
    return query.offset(skip).limit(limit).all()

@app.get("/api/clinics/{clinic_id}", response_model=schemas.ClinicDetailResponse)
def read_clinic_details(clinic_id: str, db: Session = Depends(get_db)):
    clinic = db.query(models.Clinic).filter(models.Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
        
    services = db.query(models.Price).filter(models.Price.clinic_id == clinic_id).all()
    doctors = db.query(models.Doctor).filter(models.Doctor.clinic_id == clinic_id).all()
    
    return schemas.ClinicDetailResponse(clinic=clinic, services=services, doctors=doctors)

@app.get("/api/services", response_model=List[schemas.Service])
def read_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Service).offset(skip).limit(limit).all()

@app.get("/api/prices/{service_id}", response_model=List[schemas.Price])
def read_prices_for_service(service_id: str, city: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Price).filter(models.Price.service_id == service_id)
    if city:
        query = query.join(models.Clinic).filter(models.Clinic.city == city)
    return query.all()

# --- Subscriptions API ---
@app.post("/api/subscriptions", response_model=schemas.SubscriptionResponse)
def subscribe(sub: schemas.SubscriptionCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(models.UserSubscription).filter(
        models.UserSubscription.user_id == current_user.id,
        models.UserSubscription.service_id == sub.service_id,
        models.UserSubscription.clinic_id == sub.clinic_id
    ).first()
    
    if existing:
        return existing
        
    new_sub = models.UserSubscription(
        user_id=current_user.id,
        service_id=sub.service_id,
        clinic_id=sub.clinic_id
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return new_sub

@app.get("/api/subscriptions", response_model=List[schemas.SubscriptionResponse])
def get_my_subscriptions(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.UserSubscription).filter(models.UserSubscription.user_id == current_user.id).all()


