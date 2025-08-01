import unittest
from unittest.mock import patch, Mock
import requests
import sys
import os

# Add the parent directory (StarWars_ToDo root) to the Python path to import swapi module
# Current file is in StarWars_ToDo/tests/, we need to go up one level to StarWars_ToDo/
current_dir = os.path.dirname(os.path.abspath(__file__))  # /path/to/StarWars_ToDo/tests
project_root = os.path.dirname(current_dir)  # /path/to/StarWars_ToDo
sys.path.insert(0, project_root)

try:
    from swapi import (
        fetch_from_swapi,
        get_all_items_from_endpoint,
        get_random_character,
        get_random_planet,
        get_random_starship,
        get_random_vehicle,
        clear_cache,
        get_cache_info,
        CACHE,
        SWAPI_ENDPOINTS
    )
except ImportError as e:
    print(f"Error importing swapi module: {e}")
    print("Current directory:", os.getcwd())
    print("Test file location:", current_dir)
    print("Looking for swapi.py in project root:", project_root)

    # Check if swapi.py exists in project root
    swapi_path = os.path.join(project_root, 'swapi.py')
    if os.path.exists(swapi_path):
        print(f"✓ Found swapi.py at: {swapi_path}")
    else:
        print(f"✗ swapi.py not found at: {swapi_path}")
        print("Files in project root:", [f for f in os.listdir(project_root) if f.endswith('.py')])

    print("\nPlease ensure:")
    print("1. swapi.py is in the StarWars_ToDo/ root directory")
    print("2. test_swapi.py is in the StarWars_ToDo/tests/ subdirectory")
    print("3. Use one of these commands:")
    print("   From StarWars_ToDo/: python -m tests.test_swapi")
    print("   From StarWars_ToDo/: python tests/test_swapi.py")
    print("   From tests/: python test_swapi.py")
    sys.exit(1)


class TestSwapiModule(unittest.TestCase):
    """Test suite for swapi.py module."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear cache before each test
        clear_cache()

    def tearDown(self):
        """Clean up after each test method."""
        # Clear cache after each test
        clear_cache()


class TestFetchFromSwapi(TestSwapiModule):
    """Test cases for fetch_from_swapi function."""

    @patch('swapi.requests.get')
    def test_fetch_from_swapi_success_list_endpoint(self, mock_get):
        """Test successful fetch from list endpoint."""
        # Mock response data
        mock_response_data = {
            "results": [
                {"properties": {"name": "Luke Skywalker"}},
                {"properties": {"name": "Darth Vader"}}
            ],
            "next": "https://swapi.tech/api/people?page=2",
            "previous": None,
            "count": 82
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test the function
        result = fetch_from_swapi('people', page=1)

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(len(result['results']), 2)
        self.assertEqual(result['count'], 82)
        self.assertIsNotNone(result['next'])
        self.assertIsNone(result['previous'])

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{SWAPI_ENDPOINTS['people']}?page=1&limit=10",
            timeout=10
        )

    @patch('swapi.requests.get')
    def test_fetch_from_swapi_success_single_endpoint(self, mock_get):
        """Test successful fetch from single item endpoint."""
        # Mock response data for single item
        mock_response_data = {
            "result": {"properties": {"name": "Luke Skywalker"}}
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test the function
        result = fetch_from_swapi('people', page=1)

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['count'], 1)
        self.assertIsNone(result['next'])
        self.assertIsNone(result['previous'])

    @patch('swapi.requests.get')
    def test_fetch_from_swapi_caching(self, mock_get):
        """Test that caching works correctly."""
        # Mock response data
        mock_response_data = {
            "results": [{"properties": {"name": "Luke Skywalker"}}],
            "next": None,
            "previous": None,
            "count": 1
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # First call
        result1 = fetch_from_swapi('people', page=1)

        # Second call should use cache
        result2 = fetch_from_swapi('people', page=1)

        # Assertions
        self.assertEqual(result1, result2)
        # Should only make one HTTP request due to caching
        mock_get.assert_called_once()

    def test_fetch_from_swapi_invalid_endpoint(self):
        """Test handling of invalid endpoint."""
        result = fetch_from_swapi('invalid_endpoint')
        self.assertIsNone(result)

    @patch('swapi.requests.get')
    def test_fetch_from_swapi_request_timeout(self, mock_get):
        """Test handling of request timeout."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")

        result = fetch_from_swapi('people')
        self.assertIsNone(result)

    @patch('swapi.requests.get')
    def test_fetch_from_swapi_request_exception(self, mock_get):
        """Test handling of request exceptions."""
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        result = fetch_from_swapi('people')
        self.assertIsNone(result)

    @patch('swapi.requests.get')
    def test_fetch_from_swapi_invalid_json(self, mock_get):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_from_swapi('people')
        self.assertIsNone(result)

    @patch('swapi.requests.get')
    def test_fetch_from_swapi_retry_mechanism(self, mock_get):
        """Test retry mechanism on failure."""
        # First two calls fail, third succeeds
        mock_get.side_effect = [
            requests.exceptions.RequestException("Error 1"),
            requests.exceptions.RequestException("Error 2"),
            Mock(json=lambda: {"results": []}, raise_for_status=lambda: None)
        ]

        result = fetch_from_swapi('people')
        self.assertIsNotNone(result)
        self.assertEqual(mock_get.call_count, 3)

    @patch('swapi.requests.get')
    def test_fetch_from_swapi_unexpected_response_format(self, mock_get):
        """Test handling of unexpected response format."""
        mock_response_data = {
            "unexpected_field": "value"
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_from_swapi('people')
        self.assertIsNone(result)


class TestGetAllItemsFromEndpoint(TestSwapiModule):
    """Test cases for get_all_items_from_endpoint function."""

    @patch('swapi.fetch_from_swapi')
    def test_get_all_items_single_page(self, mock_fetch):
        """Test getting all items from single page."""
        mock_fetch.return_value = {
            "results": [
                {"properties": {"name": "Luke Skywalker"}},
                {"properties": {"name": "Darth Vader"}}
            ],
            "next": None,
            "count": 2
        }

        result = get_all_items_from_endpoint('people', max_items=10)

        self.assertEqual(len(result), 2)
        mock_fetch.assert_called_once_with('people', 1)

    @patch('swapi.fetch_from_swapi')
    def test_get_all_items_multiple_pages(self, mock_fetch):
        """Test getting all items from multiple pages."""
        # Mock multiple pages
        mock_fetch.side_effect = [
            {
                "results": [{"properties": {"name": "Luke"}}],
                "next": "page2",
                "count": 3
            },
            {
                "results": [{"properties": {"name": "Leia"}}],
                "next": "page3",
                "count": 3
            },
            {
                "results": [{"properties": {"name": "Han"}}],
                "next": None,
                "count": 3
            }
        ]

        result = get_all_items_from_endpoint('people', max_items=10)

        self.assertEqual(len(result), 3)
        self.assertEqual(mock_fetch.call_count, 3)

    @patch('swapi.fetch_from_swapi')
    def test_get_all_items_max_items_limit(self, mock_fetch):
        """Test max_items limit is respected."""
        mock_fetch.return_value = {
            "results": [
                {"properties": {"name": "Luke"}},
                {"properties": {"name": "Leia"}},
                {"properties": {"name": "Han"}}
            ],
            "next": None,
            "count": 3
        }

        result = get_all_items_from_endpoint('people', max_items=2)

        self.assertEqual(len(result), 2)

    @patch('swapi.fetch_from_swapi')
    def test_get_all_items_caching(self, mock_fetch):
        """Test that caching works for get_all_items_from_endpoint."""
        mock_fetch.return_value = {
            "results": [{"properties": {"name": "Luke"}}],
            "next": None,
            "count": 1
        }

        # First call
        result1 = get_all_items_from_endpoint('people')

        # Second call should use cache
        result2 = get_all_items_from_endpoint('people')

        self.assertEqual(result1, result2)
        # Should only call fetch_from_swapi once
        mock_fetch.assert_called_once()

    @patch('swapi.fetch_from_swapi')
    def test_get_all_items_fetch_failure(self, mock_fetch):
        """Test handling when fetch_from_swapi fails."""
        mock_fetch.return_value = None

        result = get_all_items_from_endpoint('people')

        self.assertEqual(result, [])

    @patch('swapi.fetch_from_swapi')
    def test_get_all_items_empty_results(self, mock_fetch):
        """Test handling of empty results."""
        mock_fetch.return_value = {
            "results": [],
            "next": None,
            "count": 0
        }

        result = get_all_items_from_endpoint('people')

        self.assertEqual(result, [])


class TestGetRandomCharacter(TestSwapiModule):
    """Test cases for get_random_character function."""

    @patch('swapi.get_all_items_from_endpoint')
    @patch('swapi.random.choice')
    def test_get_random_character_success(self, mock_choice, mock_get_all):
        """Test successful random character retrieval."""
        mock_characters = [
            {"properties": {"name": "Luke Skywalker"}},
            {"properties": {"name": "Darth Vader"}}
        ]
        mock_get_all.return_value = mock_characters
        mock_choice.return_value = mock_characters[0]

        result = get_random_character()

        self.assertEqual(result, "Luke Skywalker")
        mock_get_all.assert_called_once_with('people')
        mock_choice.assert_called_once_with(mock_characters)

    @patch('swapi.get_all_items_from_endpoint')
    @patch('swapi.random.choice')
    def test_get_random_character_direct_name(self, mock_choice, mock_get_all):
        """Test character retrieval when name is directly in object."""
        mock_characters = [
            {"name": "Luke Skywalker"}  # Direct name field
        ]
        mock_get_all.return_value = mock_characters
        mock_choice.return_value = mock_characters[0]

        result = get_random_character()

        self.assertEqual(result, "Luke Skywalker")

    @patch('swapi.get_all_items_from_endpoint')
    @patch('swapi.random.choice')
    def test_get_random_character_fallback(self, mock_choice, mock_get_all):
        """Test fallback when API returns no characters."""
        mock_get_all.return_value = []
        mock_choice.return_value = "Luke Skywalker"

        result = get_random_character()

        self.assertEqual(result, "Luke Skywalker")
        # Should call choice twice: once for empty list, once for fallback
        self.assertEqual(mock_choice.call_count, 1)

    @patch('swapi.get_all_items_from_endpoint')
    @patch('swapi.random.choice')
    def test_get_random_character_exception_handling(self, mock_choice, mock_get_all):
        """Test exception handling in get_random_character."""
        mock_get_all.side_effect = Exception("API Error")
        mock_choice.return_value = "Luke Skywalker"

        result = get_random_character()

        self.assertEqual(result, "Luke Skywalker")

    @patch('swapi.get_all_items_from_endpoint')
    @patch('swapi.random.choice')
    def test_get_random_character_empty_name(self, mock_choice, mock_get_all):
        """Test handling of empty/None name."""
        mock_characters = [
            {"properties": {"name": ""}},  # Empty name
            {"properties": {"name": None}}  # None name
        ]
        mock_get_all.return_value = mock_characters
        mock_choice.side_effect = [mock_characters[0], "Luke Skywalker"]

        result = get_random_character()

        self.assertEqual(result, "Luke Skywalker")


class TestGetRandomPlanet(TestSwapiModule):
    """Test cases for get_random_planet function."""

    @patch('swapi.get_all_items_from_endpoint')
    @patch('swapi.random.choice')
    def test_get_random_planet_success(self, mock_choice, mock_get_all):
        """Test successful random planet retrieval."""
        mock_planets = [
            {"properties": {"name": "Tatooine"}},
            {"properties": {"name": "Alderaan"}}
        ]
        mock_get_all.return_value = mock_planets
        mock_choice.return_value = mock_planets[0]

        result = get_random_planet()

        self.assertEqual(result, "Tatooine")
        mock_get_all.assert_called_once_with('planets')

    @patch('swapi.get_all_items_from_endpoint')
    @patch('swapi.random.choice')
    def test_get_random_planet_fallback(self, mock_choice, mock_get_all):
        """Test fallback when API returns no planets."""
        mock_get_all.return_value = []
        mock_choice.return_value = "Tatooine"

        result = get_random_planet()

        self.assertEqual(result, "Tatooine")


class TestGetRandomStarship(TestSwapiModule):
    """Test cases for get_random_starship function."""

    @patch('swapi.get_all_items_from_endpoint')
    @patch('swapi.random.choice')
    def test_get_random_starship_success(self, mock_choice, mock_get_all):
        """Test successful random starship retrieval."""
        mock_starships = [
            {"properties": {"name": "Millennium Falcon"}},
            {"properties": {"name": "X-wing"}}
        ]
        mock_get_all.return_value = mock_starships
        mock_choice.return_value = mock_starships[0]

        result = get_random_starship()

        self.assertEqual(result, "Millennium Falcon")
        mock_get_all.assert_called_once_with('starships')

    @patch('swapi.get_all_items_from_endpoint')
    @patch('swapi.random.choice')
    def test_get_random_starship_fallback(self, mock_choice, mock_get_all):
        """Test fallback when API returns no starships."""
        mock_get_all.return_value = []
        mock_choice.return_value = "Millennium Falcon"

        result = get_random_starship()

        self.assertEqual(result, "Millennium Falcon")


class TestGetRandomVehicle(TestSwapiModule):
    """Test cases for get_random_vehicle function."""

    @patch('swapi.get_all_items_from_endpoint')
    @patch('swapi.random.choice')
    def test_get_random_vehicle_success(self, mock_choice, mock_get_all):
        """Test successful random vehicle retrieval."""
        mock_vehicles = [
            {"properties": {"name": "Speeder Bike"}},
            {"properties": {"name": "AT-AT"}}
        ]
        mock_get_all.return_value = mock_vehicles
        mock_choice.return_value = mock_vehicles[0]

        result = get_random_vehicle()

        self.assertEqual(result, "Speeder Bike")
        mock_get_all.assert_called_once_with('vehicles')

    @patch('swapi.get_all_items_from_endpoint')
    @patch('swapi.random.choice')
    def test_get_random_vehicle_fallback(self, mock_choice, mock_get_all):
        """Test fallback when API returns no vehicles."""
        mock_get_all.return_value = []
        mock_choice.return_value = "Speeder Bike"

        result = get_random_vehicle()

        self.assertEqual(result, "Speeder Bike")


class TestCacheUtilities(TestSwapiModule):
    """Test cases for cache utility functions."""

    def test_clear_cache(self):
        """Test cache clearing functionality."""
        # Add some data to cache
        CACHE['test_key'] = 'test_value'
        self.assertEqual(len(CACHE), 1)

        # Clear cache
        clear_cache()

        # Verify cache is empty
        self.assertEqual(len(CACHE), 0)

    def test_get_cache_info_empty(self):
        """Test cache info with empty cache."""
        result = get_cache_info()

        expected = {
            'cache_size': 0,
            'cached_endpoints': [],
            'total_cached_items': 0
        }

        self.assertEqual(result, expected)

    def test_get_cache_info_with_data(self):
        """Test cache info with cached data."""
        # Add some test data to cache
        CACHE['people_page_1'] = {'results': [1, 2, 3]}  # dict with 'results' key = 1 item
        CACHE['planets_all_items'] = [1, 2, 3, 4, 5]  # list = 5 items
        CACHE['single_item'] = 'test'  # string = 1 item

        result = get_cache_info()

        self.assertEqual(result['cache_size'], 3)
        self.assertEqual(len(result['cached_endpoints']), 3)
        self.assertIn('people_page_1', result['cached_endpoints'])
        self.assertIn('planets_all_items', result['cached_endpoints'])
        self.assertIn('single_item', result['cached_endpoints'])
        # 1 (dict counts as 1) + 5 (list length) + 1 (single item) = 7
        self.assertEqual(result['total_cached_items'], 7)


class TestIntegration(TestSwapiModule):
    """Integration tests for the swapi module."""

    @patch('swapi.requests.get')
    def test_full_workflow_success(self, mock_get):
        """Test complete workflow from API call to random selection."""
        # Mock API response
        mock_response_data = {
            "results": [
                {"properties": {"name": "Luke Skywalker"}},
                {"properties": {"name": "Darth Vader"}}
            ],
            "next": None,
            "count": 2
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test the full workflow
        character = get_random_character()

        # Verify result
        self.assertIn(character, ["Luke Skywalker", "Darth Vader"])

        # Verify cache is populated
        cache_info = get_cache_info()
        self.assertGreater(cache_info['cache_size'], 0)

    @patch('swapi.requests.get')
    def test_fallback_behavior_on_api_failure(self, mock_get):
        """Test that fallback works when API completely fails."""
        mock_get.side_effect = requests.exceptions.RequestException("API Down")

        # All functions should return fallback values
        character = get_random_character()
        planet = get_random_planet()
        starship = get_random_starship()
        vehicle = get_random_vehicle()

        # All should return valid strings from fallback lists
        self.assertIsInstance(character, str)
        self.assertIsInstance(planet, str)
        self.assertIsInstance(starship, str)
        self.assertIsInstance(vehicle, str)

        # Verify they're not empty
        self.assertNotEqual(character.strip(), "")
        self.assertNotEqual(planet.strip(), "")
        self.assertNotEqual(starship.strip(), "")
        self.assertNotEqual(vehicle.strip(), "")


if __name__ == '__main__':
    # Configure test runner
    unittest.main(verbosity=2, buffer=True)
