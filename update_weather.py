import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

async def fetch_weather():
    async with async_playwright() as p:
        # اجرای مرورگر به صورت Headless (بدون رابط گرافیکی)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # رفتن به سایت و صبر کردن تا لود کامل شود
            await page.goto("https://www.golestanmet.ir/", timeout=30000, wait_until="networkidle")
            
            # صبر برای اینکه عناصر اصلی حتماً لود شوند
            await page.wait_for_timeout(5000)
            
            weather_data = {}
            
            # استخراج داده‌ها با استفاده از JavaScript درون صفحه
            weather_data['headline'] = await page.evaluate('''
                () => {
                    const el = document.querySelector('.headline');
                    if (!el) return "—";
                    const spans = el.querySelectorAll('span');
                    if (spans.length >= 2) return spans[0].innerText.trim() + " | " + spans[1].innerText.trim();
                    return el.innerText.trim();
                }
            ''')
            
            weather_data['lede'] = await page.evaluate('''
                () => {
                    const el = document.querySelector('.lede');
                    return el ? el.innerText.trim() : "در حال دریافت اطلاعات…";
                }
            ''')
            
            weather_data['temp'] = await page.evaluate('''
                () => {
                    const el = document.querySelector('#nowT') || document.querySelector('.now-t .num');
                    return el ? el.innerText.trim() : "0";
                }
            ''')
            
            weather_data['feelsLike'] = await page.evaluate('''
                () => {
                    const el = document.querySelector('#nowF');
                    return el ? el.innerText.trim() : "—";
                }
            ''')
            
            weather_data['condition'] = await page.evaluate('''
                () => {
                    const el = document.querySelector('#nowC');
                    return el ? el.innerText.trim() : "—";
                }
            ''')
            
            weather_data['icon'] = await page.evaluate('''
                () => {
                    const el = document.querySelector('#nowI');
                    return el ? el.src : "https://www.golestanmet.ir/wp-content/plugins/glm-portal/site/icons/cloud.png";
                }
            ''')
            
            weather_data['last_update'] = datetime.now().isoformat()
            
            # ذخیره در فایل JSON
            with open('weather.json', 'w', encoding='utf-8') as f:
                json.dump(weather_data, f, ensure_ascii=False, indent=2)
            
            print("اطلاعات هوا با موفقیت استخراج شد:", weather_data)
            
        except Exception as e:
            print(f"خطا در استخراج اطلاعات: {e}")
            raise
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_weather())
