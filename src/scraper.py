import time
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from src.operations import wait_for_element, select_coordinates_option, enter_coordinates, detect_airport_zone

def run_scraper(coordinates):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")  # <- REQUIRED for Docker
    chrome_options.add_argument("--disable-dev-shm-usage")  # <- Avoids crashes in Docker
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get("https://digitalsky.dgca.gov.in/airspace-map/#/app")
        wait_for_element(driver, By.NAME, "city")
        select_coordinates_option(driver)
        wait_for_element(driver, By.ID, "auto")
        enter_coordinates(driver, coordinates)
        time.sleep(5)
        
        screenshot_uri = take_screenshot_auto_crop_center(driver, 0.5, coordinates)
        detected_zones, zones_info = detect_airport_zone(driver)

    finally:
        driver.quit()
        
    red_zone_types = {"Airspace - Red Zone", "Airport Red"}
    filtered_zones_info = [zone for zone in zones_info if zone["zone_detail"] in red_zone_types]

    
    return {
        "zones": detected_zones,
        "zones_info": filtered_zones_info,
        "screenshot_uri": screenshot_uri
    }


def take_screenshot_auto_crop_center(driver, crop_percent, coordinates):
    try:
        png_bytes = driver.get_screenshot_as_png()
        image = Image.open(BytesIO(png_bytes))
        w, h = image.size

        new_w = int(w * crop_percent)
        new_h = int(h * crop_percent)

        left = (w - new_w) // 2
        top = (h - new_h) // 2
        right = left + new_w
        bottom = top + new_h

        display_img = image.crop((left, top, right, bottom))

        # Draw caption
        display_img_copy = display_img.copy()
        draw = ImageDraw.Draw(display_img_copy)
        caption = f"Zones for coordinates {coordinates}"
        font = ImageFont.load_default()
        bbox = draw.textbbox((10, 10), caption, font)
        draw.rectangle(bbox, fill="white")
        draw.text((10, 10), caption, fill="black", font=font)

        # Encode to base64 URI
        buf = BytesIO()
        display_img_copy.save(buf, format='PNG')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        img_uri = f"data:image/png;base64,{img_base64}"

        return img_uri

    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None