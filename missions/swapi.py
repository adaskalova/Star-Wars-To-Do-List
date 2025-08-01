import requests
import random
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Cache for API responses
CACHE = {}

# API Configuration
SWAPI_BASE = "https://www.swapi.tech/api"
SWAPI_ENDPOINTS = {
    "films": f"{SWAPI_BASE}/films",
    "people": f"{SWAPI_BASE}/people",
    "planets": f"{SWAPI_BASE}/planets",
    "species": f"{SWAPI_BASE}/species",
    "starships": f"{SWAPI_BASE}/starships",
    "vehicles": f"{SWAPI_BASE}/vehicles"
}

# Request configuration
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3


def fetch_from_swapi(endpoint, page=1, max_pages=5):
    """
    Fetch data from SWAPI with pagination support and error handling.

    Args:
        endpoint (str): API endpoint (people, planets, etc.)
        page (int): Page number to fetch
        max_pages (int): Maximum pages to fetch

    Returns:
        dict: API response data or None if failed
    """
    cache_key = f"{endpoint}_page_{page}"

    # Check cache first
    if cache_key in CACHE:
        logger.debug(f"Using cached data for {cache_key}")
        return CACHE[cache_key]

    if endpoint not in SWAPI_ENDPOINTS:
        logger.error(f"Invalid endpoint: {endpoint}")
        return None

    url = f"{SWAPI_ENDPOINTS[endpoint]}?page={page}&limit=10"

    for attempt in range(MAX_RETRIES):
        try:
            logger.debug(f"Fetching from {url} (attempt {attempt + 1})")
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            data = response.json()

            # SWAPI.tech returns data in different format
            # Check if response has 'results' (list endpoint) or 'result' (single item)
            if 'results' in data:
                # List endpoint response
                processed_data = {
                    'results': data['results'],
                    'next': data.get('next'),
                    'previous': data.get('previous'),
                    'count': data.get('count', 0)
                }
            elif 'result' in data:
                # Single item endpoint response
                processed_data = {
                    'results': [data['result']],
                    'next': None,
                    'previous': None,
                    'count': 1
                }
            else:
                logger.error(f"Unexpected response format from {url}")
                return None

            # Cache the response
            CACHE[cache_key] = processed_data
            logger.debug(f"Successfully fetched and cached {cache_key}")

            return processed_data

        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed for {url} (attempt {attempt + 1}): {e}")
            if attempt == MAX_RETRIES - 1:
                logger.error(f"All {MAX_RETRIES} attempts failed for {url}")
                return None

        except ValueError as e:
            logger.error(f"Invalid JSON response from {url}: {e}")
            return None

    return None


def get_all_items_from_endpoint(endpoint, max_items=50):
    """
    Get multiple items from an endpoint by fetching multiple pages.

    Args:
        endpoint (str): API endpoint
        max_items (int): Maximum number of items to collect

    Returns:
        list: List of items or empty list if failed
    """
    cache_key = f"{endpoint}_all_items"

    if cache_key in CACHE:
        return CACHE[cache_key]

    all_items = []
    page = 1

    while len(all_items) < max_items:
        data = fetch_from_swapi(endpoint, page)

        if not data or not data.get('results'):
            break

        items = data.get('results', [])
        all_items.extend(items)

        # Check if there are more pages
        # SWAPI.tech uses 'next' in the response to indicate more pages
        if not data.get('next') or page >= 3:  # Limit to 3 pages max for faster response
            break

        page += 1

    # Cache the collected items
    CACHE[cache_key] = all_items[:max_items]
    return all_items[:max_items]


def get_random_character():
    """
    Get a random character name from the Star Wars API.

    Returns:
        str: Random character name
    """
    try:
        characters = get_all_items_from_endpoint('people')

        if characters:
            character = random.choice(characters)
            # SWAPI.tech format: data is in 'properties' object
            properties = character.get('properties', {})
            name = properties.get('name')

            if name and name.strip():
                logger.debug(f"Selected random character: {name}")
                return name
            else:
                # Fallback: try to get name directly (in case format changes)
                name = character.get('name')
                if name and name.strip():
                    logger.debug(f"Selected random character (direct): {name}")
                    return name

        logger.warning("No characters found in API response, using fallback")

    except Exception as e:
        logger.error(f"Error getting random character: {e}")

    # Fallback to well-known Star Wars characters
    fallback_characters = [
        "Luke Skywalker", "Darth Vader", "Princess Leia", "Han Solo",
        "Obi-Wan Kenobi", "Yoda", "Chewbacca", "R2-D2", "C-3PO",
        "Mace Windu", "Qui-Gon Jinn", "Padmé Amidala", "Anakin Skywalker",
        "Ahsoka Tano", "Darth Revan", "Kyle Katarn", "Jango Fett",
        "Boba Fett", "Emperor Palpatine", "Darth Maul"
    ]

    selected = random.choice(fallback_characters)
    logger.debug(f"Using fallback character: {selected}")
    return selected


def get_random_planet():
    """
    Get a random planet name from the Star Wars API.

    Returns:
        str: Random planet name
    """
    try:
        planets = get_all_items_from_endpoint('planets')

        if planets:
            planet = random.choice(planets)
            # SWAPI.tech format: data is in 'properties' object
            properties = planet.get('properties', {})
            name = properties.get('name')

            if name and name.strip():
                logger.debug(f"Selected random planet: {name}")
                return name
            else:
                # Fallback: try to get name directly
                name = planet.get('name')
                if name and name.strip():
                    logger.debug(f"Selected random planet (direct): {name}")
                    return name

        logger.warning("No planets found in API response, using fallback")

    except Exception as e:
        logger.error(f"Error getting random planet: {e}")

    # Fallback to well-known Star Wars planets
    fallback_planets = [
        "Tatooine", "Alderaan", "Yavin 4", "Hoth", "Dagobah",
        "Bespin", "Endor", "Coruscant", "Naboo", "Kamino",
        "Geonosis", "Utapau", "Kashyyyk", "Mustafar", "Dantooine",
        "Korriban", "Tython", "Jakku", "Starkiller Base", "Crait"
    ]

    selected = random.choice(fallback_planets)
    logger.debug(f"Using fallback planet: {selected}")
    return selected


def get_random_starship():
    """
    Get a random starship name from the Star Wars API.

    Returns:
        str: Random starship name
    """
    try:
        starships = get_all_items_from_endpoint('starships')

        if starships:
            starship = random.choice(starships)
            # SWAPI.tech format: data is in 'properties' object
            properties = starship.get('properties', {})
            name = properties.get('name')

            if name and name.strip():
                logger.debug(f"Selected random starship: {name}")
                return name
            else:
                # Fallback: try to get name directly
                name = starship.get('name')
                if name and name.strip():
                    logger.debug(f"Selected random starship (direct): {name}")
                    return name

        logger.warning("No starships found in API response, using fallback")

    except Exception as e:
        logger.error(f"Error getting random starship: {e}")

    # Fallback to well-known Star Wars starships
    fallback_starships = [
        "Millennium Falcon", "X-wing", "TIE Fighter", "Star Destroyer",
        "Death Star", "Slave I", "Tantive IV", "Executor", "Venator",
        "Jedi Starfighter", "Naboo Starfighter", "A-wing", "B-wing",
        "Y-wing", "TIE Interceptor", "Lambda Shuttle", "Rebel Transport"
    ]

    selected = random.choice(fallback_starships)
    logger.debug(f"Using fallback starship: {selected}")
    return selected


def get_random_vehicle():
    """
    Get a random vehicle name from the Star Wars API.

    Returns:
        str: Random vehicle name
    """
    try:
        vehicles = get_all_items_from_endpoint('vehicles')

        if vehicles:
            vehicle = random.choice(vehicles)
            # SWAPI.tech format: data is in 'properties' object
            properties = vehicle.get('properties', {})
            name = properties.get('name')

            if name and name.strip():
                logger.debug(f"Selected random vehicle: {name}")
                return name
            else:
                # Fallback: try to get name directly
                name = vehicle.get('name')
                if name and name.strip():
                    logger.debug(f"Selected random vehicle (direct): {name}")
                    return name

        logger.warning("No vehicles found in API response, using fallback")

    except Exception as e:
        logger.error(f"Error getting random vehicle: {e}")

    # Fallback to well-known Star Wars vehicles
    fallback_vehicles = [
        "Speeder Bike", "AT-AT", "AT-ST", "Landspeeder", "Snowspeeder",
        "Pod Racer", "Swoop Bike", "Speeder Truck", "AT-TE", "LAAT",
        "Sand Crawler", "Sail Barge", "Dewback", "Bantha", "Tauntaun"
    ]

    selected = random.choice(fallback_vehicles)
    logger.debug(f"Using fallback vehicle: {selected}")
    return selected


def clear_cache():
    """Clear the API cache."""
    global CACHE
    CACHE.clear()
    logger.info("API cache cleared")


def get_cache_info():
    """
    Get information about the current cache state.

    Returns:
        dict: Cache statistics
    """
    return {
        'cache_size': len(CACHE),
        'cached_endpoints': list(CACHE.keys()),
        'total_cached_items': sum(len(v) if isinstance(v, list) else 1 for v in CACHE.values())
    }
