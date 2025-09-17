from datetime import timedelta
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    client = hass.data[DOMAIN][entry.entry_id]["client"]

    async def async_update_data():
        return await hass.async_add_executor_job(client.inverter_list)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="SolisCloud",
        update_method=async_update_data,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()

    sensors = []
    if coordinator.data and coordinator.data.get("data", {}).get("page", {}).get("records"):
        record = coordinator.data["data"]["page"]["records"][0]

        sensor_map = {
            "etoday": ("Energy Today", "kWh"),
            "etotal1": ("Total Energy", "kWh"),
            "gridPurchasedTodayEnergy": ("Grid Purchased Today", "kWh"),
            "gridSellTodayEnergy": ("Grid Sell Today", "kWh"),
            "batteryTodayChargeEnergy": ("Battery Charge Today", "kWh"),
            "batteryTodayDischargeEnergy": ("Battery Discharge Today", "kWh"),
            "homeLoadTodayEnergy": ("Home Load Today", "kWh"),
        }

        for key, (name, unit) in sensor_map.items():
            sensors.append(SolisSensor(coordinator, key, name, unit))

    async_add_entities(sensors)

class SolisSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, name, unit):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"Solis {name}"
        self._attr_unique_id = f"solis_{key}"
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        record = (
            self.coordinator.data
            .get("data", {})
            .get("page", {})
            .get("records", [])[0]
        )
        return record.get(self._key)
