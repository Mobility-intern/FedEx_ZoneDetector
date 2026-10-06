from unittest.mock import patch, Mock

class TestDetectZonesAPI:

    def test_detect_zones_no_parameters(self, client):
        response = client.get("/detect_zones")
        assert response.status_code == 400
        assert "Either coordinates or location must be provided" in response.json()["detail"]

    @patch('src.routes.check_db')
    def test_detect_zones_cached_result(self, mock_check_db, client):
        cached_result = {
            "zones": ["Airport Red"],
            "zones_info": [{"zone_name": "ZONE001", "zone_detail": "Airport Red"}],
            "screenshot_uri": "data:image/png;base64,dGVzdA=="
        }
        mock_check_db.return_value = cached_result

        response = client.get("/detect_zones?coordinates=12.9716,77.5946")
        assert response.status_code == 200
        assert response.json() == cached_result

    @patch('src.routes.Nominatim')
    @patch('src.routes.check_db')
    @patch('src.routes.write_result_to_db')
    @patch('src.routes.run_scraper')
    def test_detect_zones_location_geocoding_success(
        self,
        mock_run_scraper,
        mock_write_result_to_db,
        mock_check_db,
        mock_nominatim,
        client
    ):
        mock_check_db.return_value = None
        mock_geolocator = Mock()
        mock_location = Mock()
        mock_location.latitude = 12.9716
        mock_location.longitude = 77.5946
        mock_geolocator.geocode.return_value = mock_location
        mock_nominatim.return_value = mock_geolocator
        mock_run_scraper.return_value = {
            "zones": ["Airspace - Red Zone", "Airport Yellow(5-8Km)"],
            "zones_info": [
                {"zone_name": "ZONE123", "zone_detail": "Airspace - Red Zone"},
                {"zone_name": "ZONE124", "zone_detail": "Airport Yellow(5-8Km)"}
            ],
            "screenshot_uri": "data:image/png;base64,dGVzdA=="
        }

        response = client.get("/detect_zones?location=IIT Madras")
        assert response.status_code == 200

        result = response.json()
        assert "zones" in result
        assert "zones_info" in result
        assert "screenshot_uri" in result

        assert result["zones"] == ["Airspace - Red Zone", "Airport Yellow(5-8Km)"]
        assert result["zones_info"][0]["zone_name"] == "ZONE123"
        assert result["zones_info"][1]["zone_detail"] == "Airport Yellow(5-8Km)"
        assert result["screenshot_uri"].startswith("data:image/png;base64,")
        mock_write_result_to_db.assert_called_once()

    @patch('src.routes.Nominatim')
    @patch('src.routes.check_db', return_value=None)
    def test_detect_zones_location_not_found(self, mock_check_db, mock_nominatim, client):
        mock_geolocator = Mock()
        mock_geolocator.geocode.return_value = None  # Simulate location not found
        mock_nominatim.return_value = mock_geolocator

        response = client.get("/detect_zones?location=NonExistentPlace")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @patch('src.routes.check_db', return_value=None)
    @patch('src.routes.Nominatim')
    def test_detect_zones_geocoding_exception(self, mock_nominatim, _mock_check_db, client):
        mock_geolocator = Mock()
        mock_geolocator.geocode.side_effect = Exception("Geocoding failed")
        mock_nominatim.return_value = mock_geolocator

        response = client.get("/detect_zones?location=TestLocation")
        assert response.status_code == 500
        assert "Geocoding failed" in response.json()["detail"]
