# 🪲 NatuurSpotter

**Een interactieve webapplicatie voor het registreren, analyseren en visualiseren van keverwaarnemingen in België.**  
Gemaakt als examenopdracht voor het vak **Scripting**.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![MySQL](https://img.shields.io/badge/Database-MySQL-lightgrey)
![License](https://img.shields.io/badge/Status-Student%20Project-yellow)
![Made with Flask](https://img.shields.io/badge/Made%20with-Flask-blue)

---

## 🔍 Functionaliteiten

- ✅ **Live scraping** van keverwaarnemingen in België  
- 🗺️ **Interactieve kaart** met geolocatie (Folium)  
- 📄 **Soortendatabase** met Latijnse en Nederlandse namen, zeldzaamheidsstatus, en beschrijving  
- 📊 **Seizoensanalyse** per soort (grafiek)  
- 📥 **PDF- & CSV-export** van waarnemingsgegevens  
- 🌐 **Taalkeuze**: Nederlands 🇳🇱 en Engels 🇬🇧  
- 🧠 **AI-integratie** voor ontbrekende soortinformatie (OpenAI)  

---

## ⚙️ Technische Vereisten

- Python 3.8 of hoger  
- MySQL 5.7+ of MariaDB  
- API-sleutels:
  - [OpenAI](https://platform.openai.com/)
  - [OpenCage Geocoding](https://opencagedata.com/)

---

## 🚀 Installatie

### 1. Repository klonen
```bash
git clone https://github.com/Yorb1431/ExamenScripting-NatuurSpotter
cd ExamenScripting-NatuurSpotter
```

### 2. Dependencies installeren
```bash
pip install -r requirements.txt
```

### 3. `.env` bestand aanmaken
```env
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=natuurspotter
OPENAI_API_KEY=your_openai_key
RAPIDAPI_KEY=your_opencage_key
```

### 4. Applicatie starten
```bash
python -m NatuurSpotter.app
```

---

## 🧭 Gebruik

- Selecteer een **datum** om waarnemingen op te vragen  
- Filter op specifieke **soorten** (bv. loopkevers)  
- Klik op een waarneming voor **meer informatie**  
- Genereer rapporten als **PDF** of **CSV**  
- Analyseer **seizoenspatronen** per soort (grafiek)

---





## 📄 Licentie

Dit project is ontwikkeld als onderdeel van de opleiding **Bedrijfsmangement Applied Data Intelligence – Thomas More Hogeschool**. Gebruik is vrij voor educatieve doeleinden.

---