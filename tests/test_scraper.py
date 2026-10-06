import pytest
from unittest.mock import patch, MagicMock
from src.scraper import run_scraper, take_screenshot_auto_crop_center


class TestScraper:
    @patch("src.scraper.wait_for_element")
    @patch("src.scraper.select_coordinates_option")
    @patch("src.scraper.enter_coordinates")
    @patch("src.scraper.detect_airport_zone")
    @patch("src.scraper.webdriver.Chrome")
    @patch("src.scraper.ChromeDriverManager.install")
    def test_run_scraper(
        self,
        mock_install,
        mock_chrome,
        mock_detect_airport_zone,
        mock_enter_coordinates,
        mock_select_coordinates_option,
        mock_wait_for_element,
        mock_driver
    ):
        mock_chrome.return_value = mock_driver

        mock_detect_airport_zone.return_value = (
            ["Zone A", "Zone B"],
            [
                {"zone_detail": "Airspace - Red Zone", "info": "Restricted"},
                {"zone_detail": "Green Zone", "info": "Safe"},
                {"zone_detail": "Airport Red", "info": "Danger"},
            ]
        )

        coordinates = "12.9716,77.5946"
        result = run_scraper(coordinates)

        assert result["zones"] == ["Zone A", "Zone B"]
        assert result["screenshot_uri"].startswith("data:image/png;base64,")
        assert len(result["zones_info"]) == 2
        assert all(z["zone_detail"] in {"Airspace - Red Zone", "Airport Red"} for z in result["zones_info"])


class TestScreenshot:
    def test_take_screenshot_auto_crop_center_success(self, mock_driver):
        result = take_screenshot_auto_crop_center(mock_driver, 0.5, "13.0,77.0")
        assert isinstance(result, str)
        assert result.startswith("data:image/png;base64,")

    def test_take_screenshot_auto_crop_center_error(self):
        bad_driver = MagicMock()
        bad_driver.get_screenshot_as_png.side_effect = Exception("screenshot fail")
        result = take_screenshot_auto_crop_center(bad_driver, 0.5, "0,0")
        assert result is None
