# Changelog

Alle belangrijke wijzigingen in dit project worden gedocumenteerd in dit bestand.

Het format is gebaseerd op [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
en dit project houdt zich aan [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-05

### Toegevoegd
- Eerste release van SolarEdge MeterProxy voor Home Assistant
- HACS ondersteuning
- Modbus TCP/RTU server emulatie voor WattNode meters
- Ondersteuning voor SDM120, SDM230, SDM630 meters
- Generic meter ondersteuning voor testing
- Config flow voor eenvoudige configuratie via Home Assistant UI
- Real-time sensor data voor:
  - Totale actieve energie (kWh)
  - Import/export actieve energie (kWh)
  - Actief vermogen per fase (W)
  - Spanning per fase (V)
  - Stroom per fase (A)
  - Frequentie (Hz)
  - Power factor per fase
- Automatische Modbus register updates voor SolarEdge inverters
- Configureerbare CT settings en fase offsets
- Debug logging voor troubleshooting

### Functies
- **HACS Integratie**: Installeer direct via HACS
- **Config Flow**: Gebruiksvriendelijke setup via Home Assistant UI
- **Modbus Proxy**: Simuleert WattNode meters voor SolarEdge inverters
- **Multi-meter Support**: Ondersteunt verschillende meter typen
- **Real-time Monitoring**: Live meter data in Home Assistant
- **Configureerbaar**: Volledig aanpasbaar via de interface