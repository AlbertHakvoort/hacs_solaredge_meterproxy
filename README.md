# SolarEdge MeterProxy voor Home Assistant

Deze HACS integratie maakt het mogelijk om een SolarEdge MeterProxy te gebruiken binnen Home Assistant. Hiermee kun je onondersteunde kWh meters gebruiken met je SolarEdge omvormer door ze te laten fungeren als ondersteunde WattNode meters.

## Functies

- **Modbus Proxy Server**: Simuleert een WattNode meter voor je SolarEdge inverter
- **Meerdere meter ondersteuning**: Ondersteunt verschillende typen meters zoals SDM120, SDM230, SDM630 en InfluxDB
- **Real-time monitoring**: Leest en proxy't meter data in real-time naar je SolarEdge systeem
- **Home Assistant integratie**: Toont meter data als sensoren in Home Assistant
- **Configureerbaar**: Volledig configureerbaar via Home Assistant UI

## Ondersteunde Meters

- Eastron SDM120M
- Eastron SDM230M  
- Eastron SDM630M
- InfluxDB (via HTTP API)
- MQTT (voor P1 meters)
- Generieke Modbus meters

## Installatie

### Via HACS (Aanbevolen)

1. **Voeg custom repository toe aan HACS:**
   - Ga naar HACS in Home Assistant
   - Klik op de drie puntjes (⋮) rechtsboven
   - Selecteer "Custom repositories"
   - Voeg deze URL toe: `https://github.com/AlbertHakvoort/hacs_solaredge_meterproxy`
   - Selecteer categorie: "Integration"
   - Klik "Add"

2. **Installeer de integratie:**
   - Ga naar HACS > Integrations
   - Klik op "SolarEdge MeterProxy"
   - Klik "Download"
   - Herstart Home Assistant

3. **Configureer de integratie:**
   - Ga naar Instellingen > Apparaten & Services
   - Klik "Integratie toevoegen"
   - Zoek naar "SolarEdge MeterProxy"
   - Volg de configuratie stappen

### Handmatige Installatie

1. Download de laatste release
2. Kopieer de `custom_components/solaredge_meterproxy` map naar je Home Assistant `custom_components` directory
3. Herstart Home Assistant

## Configuratie

De integratie ondersteunt configuratie via de Home Assistant UI. Je kunt het volgende instellen:

### Server Instellingen
- **IP Adres**: Het IP adres waarop de Modbus server luistert (standaard: 0.0.0.0)
- **Poort**: De Modbus TCP poort (standaard: 5502)
- **Protocol**: Kies tussen Modbus RTU of TCP
- **Log Level**: Debug niveau voor troubleshooting

### Meter Configuratie
- **Meter Type**: Selecteer het type meter (SDM120, SDM230, InfluxDB, etc.)
- **Modbus Adres**: Het Modbus adres dat de SolarEdge inverter gebruikt
- **Refresh Rate**: Hoe vaak de meter wordt uitgelezen (in seconden)
- **Meter specifieke instellingen**: Afhankelijk van het meter type

## SolarEdge Inverter Setup

1. Open de SetApp applicatie
2. Ga naar de Modbus instellingen van je inverter
3. Stel RS485-1 in als "SunSpec (Non-SE Logger)"
4. Stel Device ID in op 1
5. Voeg een nieuwe meter toe:
   - Protocol: "Modbus (Multi-Device)"
   - Meter Function: Afhankelijk van je gebruik (Production/Consumption)
   - Meter Protocol: "SolarEdge" 
   - Device ID: 2 (of een ander ongebruikt ID)
   - CT Rating en Grid Topology: Volgens je situatie

## Troubleshooting

### Geen verbinding met meter
- Controleer de IP en poort instellingen
- Zorg dat de firewall de poort toestaat
- Controleer de Modbus gateway configuratie

### Inverter ziet geen meter data
- Controleer dat het Modbus adres overeenkomt tussen inverter en integratie
- Zet log level op DEBUG om meer informatie te krijgen
- Controleer de RS485 verbindingen

### Meter data komt niet binnen
- Controleer de meter configuratie (IP, poort, Modbus adres)
- Test de meter verbinding buiten Home Assistant
- Controleer netwerk verbindingen

## Support

Voor vragen en issues, gebruik de GitHub issue tracker: [Issues](https://github.com/AlbertHakvoort/hacs_solaredge_meterproxy/issues)

## Credits

Deze integratie is gebaseerd op het excellente werk van [nmakel/solaredge_meterproxy](https://github.com/nmakel/solaredge_meterproxy).