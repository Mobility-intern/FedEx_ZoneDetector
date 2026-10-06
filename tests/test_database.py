import json
import sqlite3
from src import db  
from src.init_db import init_db


class TestZoneLogsDB:
    
    def test_init_db_creates_zone_logs_table(self, temp_db):
    
        init_db()  

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='zone_logs';")
        table = cursor.fetchone()
        conn.close()

        assert table is not None
        assert table[0] == "zone_logs"


    def test_write_result_to_db(self, temp_db):
        input_type = "coordinates"
        input_value = "12.9716,77.5946"
        zones = ["Airport Red", "Red Zone"]
        zones_info = [
            {"zone_name": "DSRZONE0001", "zone_detail": "Airport Red"},
            {"zone_name": "DSRZONE0002", "zone_detail": "Red Zone"}
        ]
        screenshot_base64 = "dGVzdF9pbWFnZV9kYXRh"

        db.write_result_to_db(input_type, input_value, zones, zones_info, screenshot_base64)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM zone_logs")
        rows = cursor.fetchall()
        conn.close()

        assert len(rows) == 1
        assert rows[0][2] == input_type
        assert rows[0][3] == input_value
        assert json.loads(rows[0][4]) == zones
        assert json.loads(rows[0][5]) == ["DSRZONE0001", "DSRZONE0002"]
        assert json.loads(rows[0][6]) == ["Airport Red", "Red Zone"]
        assert rows[0][7] == screenshot_base64

    def test_check_db_existing_record(self, temp_db):
        input_type = "coordinates"
        input_value = "12.9716,77.5946"
        zones = ["Airport Red"]
        zones_info = [{"zone_name": "ZONE001", "zone_detail": "Airport Red"}]
        screenshot_base64 = "dGVzdF9pbWFnZV9kYXRh"

        db.write_result_to_db(input_type, input_value, zones, zones_info, screenshot_base64)

        result = db.check_db(input_type, input_value)

        assert result is not None
        assert result["zones"] == zones
        assert result["zones_info"] == zones_info
        assert "data:image/png;base64," in result["screenshot_uri"]

    def test_check_db_nonexistent_record(self, temp_db):
        result = db.check_db("coordinates", "0.0,0.0")
        assert result is None

    def test_check_db_green_zone(self, temp_db):
        input_type = "coordinates"
        input_value = "12.9716,77.5946"
        zones = ["Green Zone"]
        zones_info = [{"message": "No restricted zones detected. Area is in Green Zone."}]
        screenshot_base64 = "dGVzdF9pbWFnZV9kYXRh"

        db.write_result_to_db(input_type, input_value, zones, zones_info, screenshot_base64)

        result = db.check_db(input_type, input_value)

        assert result is not None
        assert result["zones"] == ["Green Zone"]
        assert result["zones_info"] == [{"message": "No restricted zones detected. Area is in Green Zone."}]
        assert "data:image/png;base64," in result["screenshot_uri"]
