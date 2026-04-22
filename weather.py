import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
CITY = input("Δώσε πόλη: ")

url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=el"

response = requests.get(url)
data = response.json()

if response.status_code == 200:
    print(f"Πόλη: {data['name']}")
    print(f"Καιρός: {data['weather'][0]['description']}")
    print(f"Θερμοκρασία: {data['main']['temp']}°C")
    print(f"Αίσθηση: {data['main']['feels_like']}°C")
    print(f"Υγρασία: {data['main']['humidity']}%")
else:
    print(f"Error: {data['message']}")