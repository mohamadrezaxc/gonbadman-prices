import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

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
        
        # ۱. استخراج عنوان (بر اساس کلاس headline)
        headline_tag = soup.find(class_='headline')
        if headline_tag:
            spans = headline_tag.find_all('span')
            if len(spans) >= 2:
                weather_data['headline'] = f"{spans[0].text.strip()} | {spans[1].text.strip()}"
            else:
                weather_data['headline'] = headline_tag.text.strip()
        else:
             weather_data['headline'] = "آسمانی ابری | و هوای آرام"

        # ۲. استخراج توضیحات (بر اساس کلاس lede)
        lede_tag = soup.find(class_='lede')
        if lede_tag:
            weather_data['lede'] = lede_tag.text.strip()
        else:
             weather_data['lede'] = "دریافت اطلاعات با موفقیت انجام نشد."

        # ۳. دمای فعلی (جستجو برای کلاس now-t و درون آن num)
        now_t = soup.find(class_='now-t')
        if now_t:
            temp_span = now_t.find(class_='num')
            if temp_span:
                # فقط اعداد را نگه می‌داریم
                temp_text = re.sub(r'[^\d۰-۹]', '', temp_span.text)
                weather_data['temp'] = temp_text if temp_text else "۱۶"

        # ۴. احساس دما
        now_f = soup.find(id='nowF') or soup.find(class_='now-s').find(class_='num') if soup.find(class_='now-s') else None
        if now_f:
            weather_data['feelsLike'] = re.sub(r'[^\d۰-۹]', '', now_f.text)
        
        # ۵. وضعیت هوا
        now_c = soup.find(id='nowC') or soup.find(class_='now-s').find('b') if soup.find(class_='now-s') else None
        if now_c:
            weather_data['condition'] = now_c.text.strip()

        # ۶. آیکون
        now_i = soup.find(id='nowI') or soup.find(class_='now-i')
        if now_i and now_i.get('src'):
            src = now_i['src']
            if src.startswith('/'):
                weather_data['icon'] = f"https://www.golestanmet.ir{src}"
            elif not src.startswith('http'):
                weather_data['icon'] = f"https://www.golestanmet.ir/{src}"
            else:
                weather_data['icon'] = src
        else:
             weather_data['icon'] = "https://www.golestanmet.ir/wp-content/plugins/glm-portal/site/icons/cloud.png"

        # زمان به‌روزرسانی
        weather_data['last_update'] = datetime.now().isoformat()
        
        # ذخیره در فایل
        with open('weather.json', 'w', encoding='utf-8') as f:
            json.dump(weather_data, f, ensure_ascii=False, indent=2)
        
        print("اطلاعات هوا با موفقیت استخراج شد:", weather_data)
        
    except Exception as e:
        print(f"خطا در استخراج اطلاعات: {e}")
        raise

if __name__ == "__main__":
    fetch_golestan_weather()
