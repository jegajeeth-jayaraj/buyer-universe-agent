import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()  # reads COMPANIES_HOUSE_API_KEY from your .env file
key = os.getenv("COMPANIES_HOUSE_API_KEY")

if not key:
    sys.exit("No API key found. Check .env contains COMPANIES_HOUSE_API_KEY=...")
if len(sys.argv) < 2:
    sys.exit("Usage: python src/test_companies_house.py COMPANY_NUMBER")

number = sys.argv[1]
url = f"https://api.company-information.service.gov.uk/company/{number}"

# Companies House uses HTTP Basic auth: the API key is the username, password is blank
resp = requests.get(url, auth=(key, ""), timeout=15)
print("Status:", resp.status_code)

if resp.status_code == 200:
    data = resp.json()
    print("Name:", data.get("company_name"))
    print("SIC codes:", data.get("sic_codes"))
    print("Incorporated:", data.get("date_of_creation"))
else:
    print(resp.text[:300])