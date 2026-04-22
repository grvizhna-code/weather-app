# 🌤️ Weather App

Απλή εφαρμογή καιρού που τρέχει από το terminal.

## Τι κάνει
- Ζητάει από τον χρήστη μια πόλη
- Συνδέεται με το OpenWeatherMap API
- Εμφανίζει θερμοκρασία, καιρό και υγρασία

## Εγκατάσταση
1. Κλωνοποίησε το repo
2. Εγκατάστησε τα dependencies
3. Φτιάξε `.env` αρχείο με το API key σου

## Χρήση
pip install -r requirements.txt
python3 weather.py

### Extra (πιο “pro” χρήση)

- **Non-interactive**:
  - `python3 weather.py --city Athens`
  - `python3 weather.py -c "Thessaloniki"`
- **Units / language**:
  - `python3 weather.py -c London --units imperial --lang en`
- **Cache** (default on, 10 λεπτά):
  - `python3 weather.py -c Athens` (χρησιμοποιεί cache)
  - `python3 weather.py -c Athens --no-cache` (πάντα live)