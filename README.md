# SolarEdge MeterProxy - P1 Smart Meter Integration

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/AlbertHakvoort/hacs_solaredge_meterproxy)](https://github.com/AlbertHakvoort/hacs_solaredge_meterproxy/releases)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Een Home Assistant integratie die je P1 slimme meter omzet naar een virtuele Modbus meter die SolarEdge inverters kunnen lezen.

## Wat doet deze integratie?

Deze integratie leest de gegevens van je bestaande **P1 slimme meter** in Home Assistant en presenteert deze als een **virtuele WattNode meter** via Modbus TCP. Hierdoor kan je SolarEdge inverter verbinding maken met je "gecertificeerde meter" terwijl je gewoon je bestaande P1 meter gebruikt.

### Het proces:
1. **P1 data lezen**: Leest power, voltage en current gegevens van je P1 meter entities
2. **Modbus server**: Draait een Modbus TCP server op je Home Assistant 
3. **WattNode emulatie**: Presenteert P1 data als WattNode meter registers
4. **SolarEdge verbinding**: SolarEdge inverter verbindt met de virtuele meter

## Vereisten

- Home Assistant met werkende P1 meter integratie (bijv. DSMR, P1 Monitor, etc.)
- SolarEdge inverter met Ethernet verbinding
- Netwerk toegang tussen SolarEdge inverter en Home Assistant

## Installatie via HACS

### Stap 1: Repository toevoegen
1. Open HACS in Home Assistant
2. Klik op de drie puntjes (⋮) rechtsboven
3. Selecteer "Custom repositories"
4. Voeg toe:
   - **Repository**: `https://github.com/AlbertHakvoort/hacs_solaredge_meterproxy`
   - **Type**: Integration
5. Klik "Add"

### Stap 2: Integratie installeren
1. Zoek naar "SolarEdge MeterProxy" in HACS
2. Klik "Download"
3. Herstart Home Assistant
4. Ga naar Settings → Devices & Services → Add Integration
5. Zoek "SolarEdge MeterProxy"

## Configuratie

### P1 Meter Entities
Configureer de volgende P1 meter entities (optioneel - laat leeg wat je niet hebt):

**Verplicht:**
- **P1 Total Power Entity**: Totaal vermogen (bijv. `sensor.power_consumed`)

**Optioneel per fase:**
- **P1 Voltage L1/L2/L3 Entity**: Spanning per fase
- **P1 Current L1/L2/L3 Entity**: Stroom per fase  
- **P1 Power L1/L2/L3 Entity**: Vermogen per fase

**Modbus instellingen:**
- **Server IP**: `0.0.0.0` (alle interfaces)
- **Server Port**: `5502` (standaard Modbus TCP poort)
- **Protocol**: `tcp`
- **Virtual Meter Address**: `2` (Modbus slave address)

## SolarEdge Configuratie

### Stap 1: Zoek je Home Assistant IP
Noteer het IP-adres van je Home Assistant (bijv. `192.168.1.100`)

### Stap 2: Configureer SolarEdge
1. Login op je SolarEdge inverter webinterface
2. Ga naar **Communication** → **Modbus**
3. Configureer:
   - **Protocol**: `Modbus TCP`
   - **IP Address**: `[Home Assistant IP]` (bijv. `192.168.1.100`)
   - **Port**: `5502`
   - **Device ID**: `2`
   - **Meter Type**: `WattNode` of `Generic`

### Stap 3: Activeer meter
1. Ga naar **Communication** → **RS485-2**
2. Selecteer **External Meter**
3. Sla configuratie op en herstart inverter

## Troubleshooting

### Geen verbinding tussen SolarEdge en Home Assistant
```bash
# Test Modbus verbinding vanaf SolarEdge netwerk
telnet [Home Assistant IP] 5502
```

### P1 entities niet gevonden
Controleer of je P1 meter entities bestaan:
1. Ga naar Developer Tools → States
2. Zoek naar entities met `power`, `voltage`, `current`
3. Noteer de exacte entity names (bijv. `sensor.power_consumed_tariff_1`)

### Logs controleren
Ga naar Settings → System → Logs en zoek naar `solaredge_meterproxy`

## Voorbeeld P1 Entities

Typische P1 meter entities die je kunt gebruiken:

```yaml
# DSMR integratie
sensor.power_consumption         # Totaal verbruik
sensor.voltage_l1               # Spanning L1
sensor.voltage_l2               # Spanning L2  
sensor.voltage_l3               # Spanning L3
sensor.current_l1               # Stroom L1
sensor.current_l2               # Stroom L2
sensor.current_l3               # Stroom L3

# P1 Monitor integratie
sensor.p1_monitor_power_consumption
sensor.p1_monitor_voltage_l1
# etc...
```

## Features

✅ **Real-time P1 data**: Directe doorgifte van je slimme meter gegevens  
✅ **WattNode compatibiliteit**: Emuleert een gecertificeerde WattNode meter  
✅ **Automatische berekeningen**: Berekent ontbrekende waarden (stroom uit vermogen/spanning)  
✅ **Home Assistant sensors**: Toont alle metergegevens in Home Assistant  
✅ **HACS integratie**: Eenvoudige installatie en updates  

## Ondersteuning

- **GitHub Issues**: [Report bugs](https://github.com/AlbertHakvoort/hacs_solaredge_meterproxy/issues)
- **Discussions**: [Ask questions](https://github.com/AlbertHakvoort/hacs_solaredge_meterproxy/discussions)

## Licentie

MIT License - zie [LICENSE](LICENSE) file.