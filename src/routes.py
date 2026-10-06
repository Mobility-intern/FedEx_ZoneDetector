from fastapi import APIRouter, Query, HTTPException
from geopy.geocoders import Nominatim
from src.db import check_db, write_result_to_db
from src.scraper import run_scraper

router = APIRouter()

@router.get("/detect_zones")
def detect_zones(
    coordinates: str = Query(None, description="Enter coordinates in format 'lat,lon'"),
    location: str = Query(None, description="Enter location name")
):
    if not coordinates and not location:
        raise HTTPException(status_code=400, detail="Either coordinates or location must be provided.")

    input_type = "coordinates" if coordinates else "keyword"
    # Normalize location to lowercase for case-insensitive matching
    input_value = coordinates if coordinates else location.lower().strip()

    # Check cache
    cached = check_db(input_type, input_value)
    if cached:
        return cached

    # Convert location to coordinates
    if location and not coordinates:
        try:
            geolocator = Nominatim(user_agent="geoapi")
            loc = geolocator.geocode(location)
            if not loc:
                raise HTTPException(status_code=404, detail=f"Location '{location}' not found.")
            coordinates = f"{loc.latitude},{loc.longitude}"
        except HTTPException:
            # Re-raise HTTPExceptions (like our 404) without modification
            raise
        except Exception as e:
            # Handle any other unexpected errors during geocoding
            raise HTTPException(status_code=500, detail=f"Geocoding failed: {str(e)}")
    

    result = run_scraper(coordinates)
    write_result_to_db(input_type, input_value, result["zones"], result["zones_info"], result["screenshot_uri"].split(",")[1])
    return result
