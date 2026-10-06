import pytest
from unittest.mock import Mock, patch
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from src.operations import (
    wait_for_element, 
    select_coordinates_option, 
    enter_coordinates, 
    detect_airport_zone
)


class TestWaitForElement:
    @patch('src.operations.WebDriverWait')
    def test_wait_for_element_success(self, mock_webdriver_wait):
        mock_driver = Mock()
        mock_element = Mock()
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = mock_element
        mock_webdriver_wait.return_value = mock_wait_instance

        result = wait_for_element(mock_driver, By.ID, "test-id")

        assert result == mock_element
        mock_webdriver_wait.assert_called_once_with(mock_driver, 10)

    @patch('src.operations.WebDriverWait')
    @patch('builtins.print')
    def test_wait_for_element_timeout(self, mock_print, mock_webdriver_wait):
        mock_driver = Mock()
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException()
        mock_webdriver_wait.return_value = mock_wait_instance

        result = wait_for_element(mock_driver, By.ID, "test-id")

        assert result is None
        mock_print.assert_called_once_with("Timeout waiting for element: test-id")


class TestSelectCoordinatesOption:
    @patch('src.operations.Select')
    def test_select_coordinates_option_success(self, mock_select_class):
        mock_driver = Mock()
        mock_select_element = Mock()
        mock_dropdown = Mock()
        
        mock_driver.find_element.return_value = mock_select_element
        mock_select_class.return_value = mock_dropdown

        select_coordinates_option(mock_driver)

        mock_driver.find_element.assert_called_once_with(By.NAME, "city")
        mock_dropdown.select_by_visible_text.assert_called_once_with("Coordinates")

    @patch('builtins.print')
    def test_select_coordinates_option_exception(self, mock_print):
        mock_driver = Mock()
        mock_driver.find_element.side_effect = Exception("Element not found")

        select_coordinates_option(mock_driver)

        mock_print.assert_called_once_with("Error selecting 'Coordinates': Element not found")


class TestEnterCoordinates:
    def test_enter_coordinates_success(self):
        mock_driver = Mock()
        mock_input_box = Mock()
        mock_search_button = Mock()
        
        mock_driver.find_element.side_effect = [mock_input_box, mock_search_button]
        coordinates = "12.9716,77.5946"

        enter_coordinates(mock_driver, coordinates)

        mock_input_box.clear.assert_called_once()
        mock_input_box.send_keys.assert_called_once_with(coordinates)
        mock_search_button.click.assert_called_once()

    @patch('builtins.print')
    def test_enter_coordinates_exception(self, mock_print):
        mock_driver = Mock()
        mock_driver.find_element.side_effect = Exception("Element not found")

        enter_coordinates(mock_driver, "12.9716,77.5946")

        mock_print.assert_called_once_with("Error entering coordinates: Element not found")


class TestDetectAirportZone:
    @patch('src.operations.time.sleep')
    def test_detect_airport_zone_with_zones(self, mock_sleep):
        mock_driver = Mock()
        mock_marker = Mock()
        mock_card = Mock()
        
        mock_driver.find_element.return_value = mock_marker
        mock_driver.find_elements.return_value = [mock_card]

        # Setup card with zone detail
        mock_zone_name = Mock()
        mock_zone_name.text = "Airport Zone"
        mock_card.find_element.return_value = mock_zone_name
        
        mock_info_box = Mock()
        mock_label = Mock()
        mock_label.text = "Zone Detail"
        mock_detail = Mock()
        mock_detail.get_attribute.return_value = "Red Zone"
        mock_info_box.find_element.side_effect = [mock_label, mock_detail]
        mock_card.find_elements.return_value = [mock_info_box]

        zones, zones_info = detect_airport_zone(mock_driver)

        mock_marker.click.assert_called_once()
        assert zones == ["Red Zone"]
        assert len(zones_info) == 1
        assert zones_info[0]["zone_name"] == "Airport Zone"
        assert zones_info[0]["zone_detail"] == "Red Zone"

    @patch('src.operations.time.sleep')
    def test_detect_airport_zone_no_zones_default_green(self, mock_sleep):
        mock_driver = Mock()
        mock_marker = Mock()
        
        mock_driver.find_element.return_value = mock_marker
        mock_driver.find_elements.return_value = []  # No cards

        zones, zones_info = detect_airport_zone(mock_driver)

        assert zones == ["Green Zone"]
        assert zones_info == []

    @patch('builtins.print')
    @patch('src.operations.time.sleep')
    def test_detect_airport_zone_exception(self, mock_sleep, mock_print):
        mock_driver = Mock()
        mock_driver.find_element.side_effect = Exception("Marker not found")

        zones, zones_info = detect_airport_zone(mock_driver)

        mock_print.assert_called_once_with("Error detecting zones: Marker not found")
        assert zones == []
        assert zones_info == []