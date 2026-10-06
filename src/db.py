import sqlite3
import json
from datetime import datetime

DB_FILE = "data/zone_logs.db"

def check_db(input_type, input_value):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT detected_zones, zone_names, zone_details, screenshot_base64 FROM zone_logs 
        WHERE input_type=? AND input_value=?
    ''', (input_type, input_value))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        zones = json.loads(result[0])
        zone_names = json.loads(result[1])
        zone_details = json.loads(result[2])
        img_base64 = result[3]   
        img_uri = f"data:image/png;base64,{img_base64}"
        
        zones_info = [
            {"zone_name": name, "zone_detail": detail}
            for name, detail in zip(zone_names, zone_details)
        ]

        # If no actual zones (Green Zone case), handle message
        if zones == ["Green Zone"] and not zones_info:
            zones_info = [{"message": "No restricted zones detected. Area is in Green Zone."}]
            
        return {
            "zones": zones,
            "zones_info": zones_info,
            "screenshot_uri": img_uri
        }
    return None

def write_result_to_db(input_type, input_value, zones, zones_info, screenshot_base64):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    zone_names = [z["zone_name"] for z in zones_info if "zone_name" in z]
    zone_details = [z["zone_detail"] for z in zones_info if "zone_detail" in z]
    cursor.execute('''
        INSERT INTO zone_logs (timestamp, input_type, input_value, detected_zones, zone_names, zone_details, screenshot_base64)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        input_type,
        input_value,
        json.dumps(zones),
        json.dumps(zone_names),
        json.dumps(zone_details),
        screenshot_base64
    ))
    conn.commit()
    conn.close()