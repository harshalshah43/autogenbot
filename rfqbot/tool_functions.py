import requests
from dotenv import load_dotenv
import os
load_dotenv()
# Helper function for Haversine distance calculation
import math
import difflib
from portlist import MAJOR_TRADING_PORTS_DATA
import random

def get_nearest_ports(address: str) -> str: # list[dict]:
    """
    Finds the nearest available ports (sea or air) to a given address using Geoapify.

    Args:
        address (str): The full delivery or pickup address.
        port_type (str, optional): The type of port to search for.
                                   Can be "sea", "air", or "any". Defaults to "any".
        limit (int, optional): The maximum number of nearest ports to return. Defaults to 5.

    Returns:
        String containing port names separated by comma
        Returns empty strings if no ports are found
    """
    port_type: str = "any"
    limit: int = 5
    GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY") # Store your API key securely
    if not GEOAPIFY_API_KEY:
        raise ValueError("GEOAPIFY_API_KEY environment variable not set.")

    # Step 1: Geocode the input address to get its coordinates
    geocode_url = "https://api.geoapify.com/v1/geocode/search"
    geocode_params = {
        "text": address,
        "apiKey": GEOAPIFY_API_KEY,
        "limit": 1 # We only need the coordinates of the input address
    }

    try:
        geocode_response = requests.get(geocode_url, params=geocode_params)
        geocode_response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        geocode_data = geocode_response.json()

        if not geocode_data or not geocode_data.get("features"):
            print(f"Could not geocode address: {address}")
            return ''

        input_location = geocode_data["features"][0]["geometry"]["coordinates"]
        input_lon, input_lat = input_location[0], input_location[1]

    except requests.exceptions.RequestException as e:
        print(f"Error during geocoding API call: {e}")
        return ''

    # Step 2: Search for nearby ports using the Places API
    places_url = "https://api.geoapify.com/v2/places"
    
    categories = []
    if port_type == "sea" or port_type == "any":
        categories.append("man_made.pier") # Category for sea ports
    if port_type == "air" or port_type == "any":
        categories.append("airport") # Category for airports
        categories.append("airport.international") # Category for airports

    if not categories:
        print(f"No valid port_type specified: {port_type}")
        return ''

    places_params = {
        "categories": ",".join(categories),
        "filter": f"circle:{input_lon},{input_lat},50000", # Search within a 50km radius initially
        "bias": f"proximity:{input_lon},{input_lat}", # Prioritize results closer to the input location
        "limit": 20, # Fetch more results to filter and sort locally
        "apiKey": GEOAPIFY_API_KEY
    }

    try:
        places_response = requests.get(places_url, params=places_params)
        places_response.raise_for_status()
        places_data = places_response.json()

        if not places_data or not places_data.get("features"):
            print(f"No ports found near {address} with type {port_type}")
            return ''

        nearest_ports = []
        for feature in places_data["features"]:
            properties = feature["properties"]
            port_coords = feature["geometry"]["coordinates"]
            port_lon, port_lat = port_coords[0], port_coords[1]

            # Calculate distance using Haversine formula (or a library like geopy)
            # distance_km = calculate_haversine_distance(input_lat, input_lon, port_lat, port_lon)

            # Determine port type based on categories
            port_category = "unknown"
            if "man_made.pier" in properties.get("categories", []):
                port_category = "sea"
            elif "airport" in properties.get("categories", []):
                port_category = "air"
            elif "airport.international" in properties.get("categories", []):
                port_category = "air_international"
            
            # Filter by port_type if specified and not 'any'
            if port_type != "any" and port_category != port_type:
                continue

            nearest_ports.append({
                "name": properties.get("name") or properties.get("formatted"),
                # "address": properties.get("formatted"),
                # "latitude": port_lat,
                # "longitude": port_lon,
                "type": port_category,
                # "distance_km": round(distance_km, 2)
            })
        
        # Sort by distance and return the top 'limit'
        # nearest_ports.sort(key=lambda x: x["distance_km"])
        # return nearest_ports[:limit]
        return '\n'.join([f"{port['name']} {port['type']}" for port in nearest_ports[:limit]])

    except requests.exceptions.RequestException as e:
        print(f"Error during Places API call: {e}")
        return ''

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in kilometers

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def find_city(place:str):
    port_data = MAJOR_TRADING_PORTS_DATA
    city_list = list(set(port['city'] for port in port_data))
    closest = difflib.get_close_matches(place, city_list, n=5, cutoff=0.7)

    if not closest:
        print(f"No close city match found for '{place}'.")


def find_ports(place:str):
    """In this tool you give a city or country and it will return ports"""

    port_data = MAJOR_TRADING_PORTS_DATA

    # Extract unique city names
    city_list = list(set(port['city'] for port in port_data))

    # Get closest city match
    closest = difflib.get_close_matches(place, city_list, n=5, cutoff=0.7)
    if not closest:
        print(f"No close city match found for '{place}'.")
        country_list = list(set(port['country'] for port in port_data))

        closest = difflib.get_close_matches(place, country_list, n=5, cutoff=0.7)

        if not closest:
            print(f"No close country found for '{place}'.")
            category_list = list(set(port['category'] for port in port_data))
            closest = difflib.get_close_matches(place, category_list, n=5, cutoff=0.6)

            if not closest:
                return f"No close country found for '{place}'."

    # Filter ports by closest matching city
    ports_in_city = []
    ports_in_country = []
    for closer in closest:
        ports_in_city.extend([port['port_name'] for port in port_data if port['city'] == closer])
        ports_in_country.extend([port['port_name'] for port in port_data if port['country'] == closer])

    major_ports = ports_in_city + ports_in_country
    return '\n'.join(major_ports)

def generate_rfqid() -> str:
    '''Generates RFQ ID'''
    return str(random.randint(1000, 9999))

# from langchain_community.tools import DuckDuckGoSearchRun
# from langchain_community.tools import TavilySearchResults
# search = DuckDuckGoSearchRun()
# search = taviliy_tool=TavilySearchResults()
# def web_search(question: str) -> str:
#     '''You can use tool to search web for port suggestions or any other purpose
#     Input: question: You can ask any question here.
#     Returns
#      string: Returns the answer as string.
#     '''
#     answer = search.invoke(question)
#     return answer

# put this line in the app2.py or app.py file for tool registration
# search_tool = FunctionTool(search,description = 'Use this Tool to ask web search question to get answers')


# Example Usage (replace with your actual API key in environment variables)
if __name__ == "__main__":
    # Set your Geoapify API key as an environment variable or replace in code (not recommended for production)
    # os.environ["GEOAPIFY_API_KEY"] = "YOUR_GEOAPIFY_API_KEY"

    # Example 1: Find nearest sea ports for Mumbai address
    address_mumbai = "Salalah Free Zone, OMAN)"
    ports = get_nearest_ports(address_mumbai)
    print(f"Nearest Sea Ports to {address_mumbai}:")
    for port in ports:
        print(f"- {port['name']} ({port['type']})") # - {port['distance_km']} km away")

    print("\n" + "="*50 + "\n")

    

    # # Example 2: Find nearest airports for Delhi address
    # address_delhi = "Rajiv Chowk, Connaught Place, New Delhi"
    # air_ports = get_nearest_ports(address_delhi, port_type="air")
    # print(f"Nearest Air Ports to {address_delhi}:")
    # for port in air_ports:
    #     print(f"- {port['name']} ({port['type']}) - {port['distance_km']} km away")

    # print("\n" + "="*50 + "\n")

    # # Example 3: Find nearest ports (any type) for a generic address
    # address_generic = "1600 Amphitheatre Parkway, Mountain View, CA"
    # any_ports = get_nearest_ports(address_generic, port_type="air", limit=3)
    # print(f"Nearest Ports (any type) to {address_generic}:")
    # for port in any_ports:
    #     print(f"- {port['name']} ({port['type']}) - {port['distance_km']} km away")