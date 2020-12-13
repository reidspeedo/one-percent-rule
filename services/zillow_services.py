from repository import zillow_repository
from services import zillow_scraper

def retrieve_properties(zip_code):
    return zillow_scraper.get_listings_for_zip(zip_code)
