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
            await page.goto("https://www.golestanmet.ir/", timeout=60000, wait_until="networkidle")
            
            # صبر اولیه برای لود شدن صفحه
            await page.wait_for_timeout(3000)
            
            # --- تلاش برای انتخاب شهر گنبدکاووس ---
            print("در حال تلاش برای انتخاب گنبدکاووس...")
            try:
                # روش ۱: کلیک روی لینک یا دکمه‌ای که متن گنبدکاووس دارد
                # (اگر در سایت گزینه‌ای برای انتخاب شهر وجود داشته باشد)
                await page.click('text=گنبدکاووس', timeout=5000)
                print("با کلیک روی متن گنبدکاووس انتخاب شد.")
            except:
                print("کلیک مستقیم ممکن نبود. تلاش برای تغییر هش آدرس...")
                # روش ۲: تغییر هش آدرس به صورت دستی
                await page.evaluate("window.location.hash = '#gonbad-e-kavus';")
                # تلاش برای ریلود کردن با هش جدید
                await page.reload(wait_until="networkidle")
            
            # صبر طولانی‌تر برای اینکه اطلاعات گنبدکاووس جایگزین گرگان شود
            print("در حال صبر برای بارگذاری کامل اطلاعات...")
            await page.wait_for_timeout(5000)
            
            # --- استخراج اطلاعات ---
            weather_data = {}
            
            # 1. عنوان
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
            
            # 2. توضیحات (Lede)
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
            
            # 6. آیکون
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
            
            # ذخیره
            with open('weather.json', 'w', encoding='utf-8') as f:
                json.dump(weather_data, f, ensure_ascii=False, indent=2)
            
            print("اطلاعات با موفقیت استخراج شد:", weather_data)
            
            # چک نهایی: آیا شهر گنبدکاووس است؟
            if "گنبد" in weather_data.get('lede', ''):
                print("✅ تایید: اطلاعات گنبدکاووس است.")
            else:
                print("⚠️ هشدار: احتمالاً اطلاعات گرگان است.")
            
        except Exception as e:
            print(f"خطا در استخراج: {e}")
            raise
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_weather())
