import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Clinic, Service, Price, PriceHistory, CategoryEnum, CurrencyEnum
from datetime import datetime

class BaseParser(ABC):
    def __init__(self):
        self.db: Session = SessionLocal()

    @abstractmethod
    def parse(self):
        """Implement parsing logic here"""
        pass

    def get_or_create_clinic(self, clinic_data: Dict[str, Any]) -> Clinic:
        clinic = self.db.query(Clinic).filter(Clinic.name == clinic_data['name']).first()
        if not clinic:
            clinic = Clinic(**clinic_data)
            self.db.add(clinic)
            self.db.commit()
            self.db.refresh(clinic)
        else:
            # Update lat/long if provided and missing
            if 'latitude' in clinic_data and clinic.latitude is None:
                clinic.latitude = clinic_data['latitude']
                clinic.longitude = clinic_data['longitude']
                self.db.commit()
        return clinic

    def get_or_create_service(self, service_data: Dict[str, Any]) -> Service:
        service = self.db.query(Service).filter(
            Service.name_raw == service_data['name_raw']
        ).first()
        if not service:
            service = Service(**service_data)
            self.db.add(service)
            self.db.commit()
            self.db.refresh(service)
        return service

    def add_or_update_price(self, price_data: Dict[str, Any]):
        price = self.db.query(Price).filter(
            Price.clinic_id == price_data['clinic_id'],
            Price.service_id == price_data['service_id']
        ).first()
        
        if price:
            old_kzt = price.price_kzt
            if float(old_kzt) != float(price_data['price_kzt']):
                price.price_kzt = price_data['price_kzt']
                price.parsed_at = datetime.utcnow()
                history = PriceHistory(price_id=price.id, old_price_kzt=old_kzt, new_price_kzt=price.price_kzt)
                self.db.add(history)
                self.db.commit()
        else:
            price = Price(**price_data)
            self.db.add(price)
            self.db.commit()
            self.db.refresh(price)
            history = PriceHistory(price_id=price.id, old_price_kzt=None, new_price_kzt=price.price_kzt)
            self.db.add(history)
            self.db.commit()

    def __del__(self):
        self.db.close()
