# HACS Integration for Solis Inverter

Custom integration to fetch data from **SolisCloud API** and expose inverter data (kWh, battery, grid, etc.) as sensors.

## Installation via HACS

1. Go to HACS → Integrations
2. Click the three dots (⋮) → **Custom repositories**
3. Add your repo URL, category = Integration
4. Search for **SolisCloud Integration** and install
5. Restart Home Assistant
6. Add the integration via `configuration.yaml` (UI support later)

```yaml
soliscloud:
  api_id: YOUR_API_ID
  api_secret: YOUR_API_SECRET
