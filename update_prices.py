import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def fetch_tgju_prices():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    prices = {}
    
    try:
        # --- 1. استخراج دلار و لیر از صفحه currency ---
        url_currency = "https://www.tgju.org/currency"
        response = requests.get(url_currency, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # دلار (استفاده از data-market-row برای دقت بیشتر)
        dollar_row = soup.find('tr', {'data-market-row': 'price_dollar_rl'})
        if dollar_row:
            dollar_td = dollar_row.find('td', class_='nf')
            if dollar_td:
                prices['dollar'] = dollar_td.text.strip()
        
        # لیر ترکیه
        lira_row = soup.find('tr', {'data-market-row': 'price_try'})
        if lira_row:
            lira_td = lira_row.find('td', class_='nf')
            if lira_td:
                prices['lira'] = lira_td.text.strip()

        # --- 2. استخراج طلای 18 عیار و سکه از صفحه اصلی ---
        url_home = "https://www.tgju.org/"
        response_home = requests.get(url_home, headers=headers, timeout=15)
        response_home.raise_for_status()
        soup_home = BeautifulSoup(response_home.text, 'html.parser')
        
        # طلای 18 عیار
        gold_li = soup_home.find('li', id='l-geram18')
        if gold_li:
            gold_price_span = gold_li.find('span', class_='info-price')
            if gold_price_span:
                prices['gold18'] = gold_price_span.text.strip()
        
        # سکه
        coin_li = soup_home.find('li', id='l-sekee')
        if coin_li:
            coin_price_span = coin_li.find('span', class_='info-price')
            if coin_price_span:
                prices['coin'] = coin_price_span.text.strip()
        
        prices['last_update'] = datetime.now().isoformat()
        
        # ذخیره در فایل JSON
        with open('prices.json', 'w', encoding='utf-8') as f:
            json.dump(prices, f, ensure_ascii=False, indent=2)
        
        print("قیمت‌ها با موفقیت استخراج و ذخیره شدند:", prices)
        
    except Exception as e:
        print(f"خطا در استخراج قیمت‌ها: {e}")
        raise

if __name__ == "__main__":
    fetch_tgju_prices()
