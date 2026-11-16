import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def fetch_golestan_weather():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    url = "https://www.golestanmet.ir/"
    weather_data = {}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # استخراج اطلاعات بر اساس ساختار سایت
        headline = soup.find('h1', id='headline')
        if headline:
            spans = headline.find_all('span')
            if len(spans) >= 2:
                weather_data['headline'] = f"{spans[0].text.strip()} | {spans[1].text.strip()}"
            else:
                weather_data['headline'] = headline.text.strip()
                
        lede = soup.find('p', id='lede')
        if lede:
            weather_data['lede'] = lede.text.strip()
            
        now_t = soup.find('span', id='nowT')
        if now_t:
            weather_data['temp'] = now_t.text.strip()
            
        now_f = soup.find('b', id='nowF')
        if now_f:
            weather_data['feelsLike'] = now_f.text.strip()
            
        now_c = soup.find('b', id='nowC')
        if now_c:
            weather_data['condition'] = now_c.text.strip()
            
        now_i = soup.find('img', id='nowI')
        if now_i and now_i.get('src'):
            src = now_i['src']
            if src.startswith('/'):
                weather_data['icon'] = f"https://www.golestanmet.ir{src}"
            elif not src.startswith('http'):
                weather_data['icon'] = f"https://www.golestanmet.ir/{src}"
            else:
                weather_data['icon'] = src

        weather_data['last_update'] = datetime.now().isoformat()
        
        with open('weather.json', 'w', encoding='utf-8') as f:
            json.dump(weather_data, f, ensure_ascii=False, indent=2)
        
        print("اطلاعات هوا با موفقیت استخراج شد.")
        
    except Exception as e:
        print(f"خطا در استخراج اطلاعات: {e}")
        raise

if __name__ == "__main__":
    fetch_golestan_weather()
