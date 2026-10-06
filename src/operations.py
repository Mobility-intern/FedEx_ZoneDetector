from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time

def wait_for_element(driver, by, identifier, timeout = 10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, identifier))
        )
    except TimeoutException:
        print(f"Timeout waiting for element: {identifier}")
        return None

def select_coordinates_option(driver):
    try:
        select_element = driver.find_element(By.NAME, "city")
        dropdown = Select(select_element)
        dropdown.select_by_visible_text("Coordinates")  
    except Exception as e:
        print(f"Error selecting 'Coordinates': {e}")

def enter_coordinates(driver, coordinates):
    try:
        input_box = driver.find_element(By.ID, "auto")
        input_box.clear()
        input_box.send_keys(coordinates)
        search_button = driver.find_element(By.CSS_SELECTOR, "button.input_search[title='Search location']")
        search_button.click()
    except Exception as e:
        print(f"Error entering coordinates: {e}")
        
def detect_airport_zone(driver):
    zones = set()
    zones_info = []
    try:
        marker = driver.find_element(By.CSS_SELECTOR, "img.leaflet-marker-icon[src$='Pin.svg']")
        marker.click()
        time.sleep(3)

        cards = driver.find_elements(By.CSS_SELECTOR, ".visual_card")
        time.sleep(2)
        
        if not cards:
            print("No restricted zones found → Green Zone.")
            return ["Green Zone"], []

        for card in cards:
            zone_name = "N/A"
            zone_detail = "N/A"
            
            try:
                zone_name = card.find_element(By.CSS_SELECTOR, ".info_heading p").text.strip()
            except:
                pass

            try:
                info_boxes = card.find_elements(By.CLASS_NAME, "info_box")
                for box in info_boxes:
                    label = box.find_element(By.TAG_NAME, "p").text.strip()
                    if label == "Zone Detail":
                        zone_detail = box.find_element(By.TAG_NAME, "h4").get_attribute("innerText").strip()
                        break
            except:
                pass
                
            if zone_detail and zone_detail.strip() and zone_detail != "N/A":
                zones.add(zone_detail.strip())

            zones_info.append({
                "zone_name": zone_name,
                "zone_detail": zone_detail
            })

    except Exception as e:
        print(f"Error detecting zones: {e}")
        
    detected_zones = list(zones)
        
    return detected_zones, zones_info