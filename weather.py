import warnings
warnings.filterwarnings("ignore")

import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=el"
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200:
        print(f"\n📍 Πόλη: {data['name']}")
        print(f"🌤️  Καιρός: {data['weather'][0]['description']}")
        print(f"🌡️  Θερμοκρασία: {data['main']['temp']}°C")
        print(f"🤔 Αίσθηση: {data['main']['feels_like']}°C")
        print(f"💧 Υγρασία: {data['main']['humidity']}%")
        print(f"💨 Άνεμος: {data['wind']['speed']} m/s")
    else:
        print(f"❌ Error: {data['message']}")

while True:
    city = input("\nΔώσε πόλη (ή 'q' για έξοδο): ")
    if city.lower() == 'q':
        print("Αντίο! 👋")
        break
    get_weather(city)