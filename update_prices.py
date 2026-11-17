import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

async def fetch_weather():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            print("در حال باز کردن سایت هواشناسی...")
            # رفتن مستقیماً به آدرس گنبدکاووس با هش
            await page.goto("https://www.golestanmet.ir/#gonbad-e-kavus", timeout=60000, wait_until="networkidle")
            
            # صبر برای رندر شدن اطلاعات
            await page.wait_for_timeout(5000)
            
            weather_data = {}
            
            # 1. استخراج عنوان
            headline_el = page.locator('.headline')
            if await headline_el.count() > 0:
                spans = headline_el.locator('span')
                if await spans.count() >= 2:
                    part1 = await spans.nth(0).inner_text()
                    part2 = await spans.nth(1).inner_text()
                    weather_data['headline'] = f"{part1.strip()} | {part2.strip()}"
                else:
                    weather_data['headline'] = (await headline_el.inner_text()).strip()
            else:
                weather_data['headline'] = "—"
            
            # 2. استخراج توضیحات (Lede)
            lede_el = page.locator('.lede')
            if await lede_el.count() > 0:
                weather_data['lede'] = (await lede_el.inner_text()).strip()
            else:
                weather_data['lede'] = "—"
            
            # 3. دمای فعلی
            temp_el = page.locator('#nowT, .now-t .num')
            if await temp_el.count() > 0:
                weather_data['temp'] = (await temp_el.first.inner_text()).strip()
            else:
                weather_data['temp'] = "0"
            
            # 4. احساس دما
            feels_el = page.locator('#nowF')
            if await feels_el.count() > 0:
                weather_data['feelsLike'] = (await feels_el.inner_text()).strip()
            else:
                weather_data['feelsLike'] = "—"
            
            # 5. وضعیت هوا
            cond_el = page.locator('#nowC')
            if await cond_el.count() > 0:
                weather_data['condition'] = (await cond_el.inner_text()).strip()
            else:
                weather_data['condition'] = "—"
            
            # 6. آدرس آیکون
            icon_el = page.locator('#nowI')
            if await icon_el.count() > 0:
                src = await icon_el.get_attribute('src')
                if src:
                    if src.startswith('/'):
                        weather_data['icon'] = f"https://www.golestanmet.ir{src}"
                    elif not src.startswith('http'):
                        weather_data['icon'] = f"https://www.golestanmet.ir/{src}"
                    else:
                        weather_data['icon'] = src
                else:
                    weather_data['icon'] = "https://www.golestanmet.ir/wp-content/plugins/glm-portal/site/icons/cloud.png"
            else:
                weather_data['icon'] = "https://www.golestanmet.ir/wp-content/plugins/glm-portal/site/icons/cloud.png"
            
            weather_data['last_update'] = datetime.now().isoformat()
            
            # ذخیره در فایل JSON
            with open('weather.json', 'w', encoding='utf-8') as f:
                json.dump(weather_data, f, ensure_ascii=False, indent=2)
            
            print("اطلاعات هوای گنبدکاووس با موفقیت استخراج شد:", weather_data)
            
        except Exception as e:
            print(f"خطا در استخراج اطلاعات: {e}")
            raise
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_weather())
