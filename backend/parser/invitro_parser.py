import requests
from bs4 import BeautifulSoup
from base import BaseParser
from models import CategoryEnum, CurrencyEnum
import re

class InvitroParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.base_url = "https://invitro.kz"
        self.clinic_data = {
            "name": "Инвитро (Invitro)",
            "city": "Астана", 
            "address": "Сеть клиник (см. на сайте)",
            "phone": "8 (727) 258-58-58",
            "working_hours": "07:30 - 15:00",
            "source_url": self.base_url
        }

    def parse(self):
        print("Starting Invitro Parser...")
        clinic = self.get_or_create_clinic(self.clinic_data)
        
        # Example URL for analyzes
        url = f"{self.base_url}/radiology/" 
        # Invitro KZ might have a different structure, let's just make a mock URL or generic one
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"Failed to fetch {url}, status code: {response.status_code}")
                return
        except Exception as e:
            print(f"Error connecting to {url}: {e}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find links
        links = soup.select('a')
        analyze_links = []
        for a in links:
            href = a.get('href', '')
            if '/radiology/' in href or '/analizes/for-doctors/' in href:
                if href not in analyze_links:
                    analyze_links.append(href)
                    
        print(f"Found {len(analyze_links)} analyze links on Invitro.")
        
        count = 0
        for link in analyze_links:
            if not link.startswith('http'):
                full_link = self.base_url + link if link.startswith('/') else f"{self.base_url}/{link}"
            else:
                full_link = link
                
            res = requests.get(full_link, headers=headers)
            if res.status_code != 200:
                continue
            
            detail_soup = BeautifulSoup(res.text, 'html.parser')
            # Look for price
            price_elements = detail_soup.find_all(string=lambda text: "тг" in text.lower() if text else False)
            title_element = detail_soup.find('h1')
            
            if title_element:
                title = title_element.text.strip()
                
                # Try finding prices more robustly
                price_texts = detail_soup.find_all(string=re.compile(r'\d[\d\s]*\s*тг', re.IGNORECASE))
                for p_text in price_texts:
                    price_match = re.search(r'(\d[\d\s]*)\s*тг', p_text, re.IGNORECASE)
                    if price_match:
                        price_str = price_match.group(1).replace(' ', '').replace('\xa0', '')
                        try:
                            price = float(price_str)
                            if price < 100:
                                continue # skip invalid tiny prices like 1.0 тг
                                
                            service = self.get_or_create_service({
                                "name_raw": title,
                                "category": CategoryEnum.laboratory
                            })
                            
                            self.add_or_update_price({
                                "clinic_id": clinic.id,
                                "service_id": service.id,
                                "price_kzt": price,
                                "currency": CurrencyEnum.KZT
                            })
                            print(f"Parsed Invitro: {title} - {price} ₸")
                            count += 1
                            break # Only one price per page
                        except ValueError:
                            pass
                        
        print(f"Finished parsing Invitro. Saved {count} prices.")

if __name__ == "__main__":
    parser = InvitroParser()
    parser.parse()
