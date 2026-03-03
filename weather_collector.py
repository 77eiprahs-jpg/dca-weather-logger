import requests
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ----------------------
# Configuration
# ----------------------
STATION = "KDCA"
LAT = 38.8512
LON = -77.0402
SHEET_NAME = "DCA Weather Logger"
CREDENTIALS_FILE = "weather_logger_credentials.json"

# ----------------------
# Google Sheets Setup
# ----------------------
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE, scope
)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# ----------------------
# NWS Observations
# ----------------------
def fetch_nws_observation():
    url = f"https://api.weather.gov/stations/{STATION}/observations/latest"
    data = requests.get(url).json()["properties"]

    temp_c = data["temperature"]["value"]
    wind_speed = data["windSpeed"]["value"]
    wind_dir = data["windDirection"]["value"]
    cloud_layers = data.get("cloudLayers", [])
    cloud_cover = cloud_layers[0].get("amount") if cloud_layers else None
    precip_mm = data.get("precipitationLastHour", {}).get("value", 0)

    temp_f = round((temp_c * 9/5) + 32, 1) if temp_c else None
    wind_mph = round(wind_speed * 2.237, 1) if wind_speed else None

    return temp_f, wind_mph, wind_dir, cloud_cover, precip_mm

# ----------------------
# NWS Forecast
# ----------------------
def fetch_nws_forecast():
    points = requests.get(f"https://api.weather.gov/points/{LAT},{LON}").json()
    forecast_url = points["properties"]["forecast"]
    periods = requests.get(forecast_url).json()["properties"]["periods"]

    for p in periods:
        if p["isDaytime"]:
            return p["temperature"]

# ----------------------
# Main Collector
# ----------------------
def collect():
    timestamp = str(datetime.utcnow())
    obs_temp, wind_speed, wind_dir, cloud_cover, precip = fetch_nws_observation()
    forecast_high = fetch_nws_forecast()

    row = [
        timestamp,
        obs_temp,
        forecast_high,
        wind_speed,
        wind_dir,
        cloud_cover,
        precip
    ]

    sheet.append_row(row)
    print("Logged:", row)

if __name__ == "__main__":
    collect()
