from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import aiohttp
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Smart Home Dashboard")
templates = Jinja2Templates(directory="app/templates")

# КОНФИГУРАЦИЯ - ТОЛЬКО ДЛЯ TEMPERATURE API ИСПРАВЛЕНА
SERVICES = {
    "temperature_api": {
        "name": "🌡️ Temperature API",
        "host": "temperature-api",      # имя сервиса в docker-compose
        "port": 8081,
        "endpoints": {
            "health": "/health",
            "info": "/info",
            "by_id": "/temperature/",          # /temperature/1
            "by_location": "/temperature"      # /temperature?location=...
        }
    },
    "sensor_service": {
        "name": "📊 Sensor Service",
        "host": "sensor-service",
        "port": 8082,
        "endpoints": {
            "health": "/api/v1/health",
            "info": "/api/v1/info",
            "sensors": "/api/v1/sensors",
            "summary": "/api/v1/summary/location"
        }
    },
    "heating_device": {
        "name": "🔥 Heating Device",
        "host": "heating-device-service",
        "port": 8083,
        "endpoints": {
            "health": "/api/v1/health",
            "info": "/api/v1/info",
            "id": "/api/v1/id",
            "status": "/api/v1/status",
            "temperature": "/api/v1/temperature"
        }
    }
}

# Кэш
cache = {
    "timestamp": datetime.now().isoformat(),
    "services": {
        "temperature_api": {
            "healthy": False,
            "info": {},
            "readings": [],
            "readings_count": 0,
            "locations": []
        },
        "sensor_service": {"healthy": False, "info": {}, "sensor_count": 0, "sensors": []},
        "heating_device": {"healthy": False, "info": {}, "status": {}, "temperature": {}}
    },
    "summaries": {}
}

async def fetch_json(session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
    """Асинхронный GET запрос"""
    try:
        logger.info(f"📡 Fetching: {url}")
        async with session.get(url, timeout=3) as response:
            if response.status == 200:
                data = await response.json()
                logger.info(f"✅ Success: {url} - {response.status}")
                return data
            else:
                logger.error(f"❌ Error {response.status}: {url}")
    except asyncio.TimeoutError:
        logger.error(f"⏱️ Timeout: {url}")
    except Exception as e:
        logger.error(f"❌ Error fetching {url}: {e}")
    return {}

# ========== ИСПРАВЛЕННАЯ ФУНКЦИЯ ДЛЯ TEMPERATURE API ==========
async def collect_temperature_api_data(session: aiohttp.ClientSession):
    """Сбор данных с Temperature API"""
    temperature_readings = []

    # 1. Получаем данные по ID датчиков (1,2,3)
    sensor_ids = ["1", "2", "3"]
    for sid in sensor_ids:
        url = f"http://{SERVICES['temperature_api']['host']}:{SERVICES['temperature_api']['port']}{SERVICES['temperature_api']['endpoints']['by_id']}{sid}"
        data = await fetch_json(session, url)
        if data and isinstance(data, dict):
            reading = {
                "sensor_id": data.get("sensor_id", sid),
                "location": data.get("location", f"Sensor {sid}"),
                "value": data.get("value", 0),
                "unit": data.get("unit", "°C"),
                "timestamp": data.get("timestamp", datetime.now().isoformat()),
                "status": data.get("status", "active"),
                "sensor_type": data.get("sensor_type", "temperature"),
                "description": data.get("description", f"Temperature sensor #{sid}")
            }
            temperature_readings.append(reading)
            logger.info(f"   ➕ Added reading from ID {sid}: {reading['value']}°C at {reading['location']}")

    # 2. Получаем данные по локациям
    locations = ["Living Room", "Bedroom", "Kitchen"]
    for loc in locations:
        url = f"http://{SERVICES['temperature_api']['host']}:{SERVICES['temperature_api']['port']}{SERVICES['temperature_api']['endpoints']['by_location']}?location={loc.replace(' ', '%20')}"
        data = await fetch_json(session, url)
        if data and isinstance(data, dict):
            # Избегаем дублирования (если такой sensor_id уже есть)
            sensor_id = data.get("sensor_id")
            exists = any(r.get("sensor_id") == sensor_id for r in temperature_readings)
            if not exists and sensor_id:
                reading = {
                    "sensor_id": sensor_id,
                    "location": data.get("location", loc),
                    "value": data.get("value", 0),
                    "unit": data.get("unit", "°C"),
                    "timestamp": data.get("timestamp", datetime.now().isoformat()),
                    "status": data.get("status", "active"),
                    "sensor_type": data.get("sensor_type", "temperature"),
                    "description": data.get("description", f"Temperature sensor in {loc}")
                }
                temperature_readings.append(reading)
                logger.info(f"   ➕ Added reading from location {loc}: {reading['value']}°C")

    # Получаем информацию о сервисе (info)
    info_url = f"http://{SERVICES['temperature_api']['host']}:{SERVICES['temperature_api']['port']}{SERVICES['temperature_api']['endpoints']['info']}"
    info_data = await fetch_json(session, info_url)

    logger.info(f"🌡️ Temperature API: collected {len(temperature_readings)} readings")
    return temperature_readings, info_data

async def collect_all_data():
    """Сбор данных со всех сервисов"""
    async with aiohttp.ClientSession() as session:
        tasks = {}

        # Temperature API - только health (info получим позже)
        tasks["temp_api_health"] = fetch_json(
            session,
            f"http://{SERVICES['temperature_api']['host']}:{SERVICES['temperature_api']['port']}{SERVICES['temperature_api']['endpoints']['health']}"
        )

        # Sensor Service
        tasks["sensor_health"] = fetch_json(
            session,
            f"http://{SERVICES['sensor_service']['host']}:{SERVICES['sensor_service']['port']}{SERVICES['sensor_service']['endpoints']['health']}"
        )
        tasks["sensor_info"] = fetch_json(
            session,
            f"http://{SERVICES['sensor_service']['host']}:{SERVICES['sensor_service']['port']}{SERVICES['sensor_service']['endpoints']['info']}"
        )
        tasks["sensor_sensors"] = fetch_json(
            session,
            f"http://{SERVICES['sensor_service']['host']}:{SERVICES['sensor_service']['port']}{SERVICES['sensor_service']['endpoints']['sensors']}"
        )

        # Heating Device
        tasks["heating_health"] = fetch_json(
            session,
            f"http://{SERVICES['heating_device']['host']}:{SERVICES['heating_device']['port']}{SERVICES['heating_device']['endpoints']['health']}"
        )
        tasks["heating_info"] = fetch_json(
            session,
            f"http://{SERVICES['heating_device']['host']}:{SERVICES['heating_device']['port']}{SERVICES['heating_device']['endpoints']['info']}"
        )
        tasks["heating_status"] = fetch_json(
            session,
            f"http://{SERVICES['heating_device']['host']}:{SERVICES['heating_device']['port']}{SERVICES['heating_device']['endpoints']['status']}"
        )
        tasks["heating_temp"] = fetch_json(
            session,
            f"http://{SERVICES['heating_device']['host']}:{SERVICES['heating_device']['port']}{SERVICES['heating_device']['endpoints']['temperature']}"
        )

        # Ждём выполнения всех параллельных задач
        results = await asyncio.gather(*tasks.values())
        result_dict = dict(zip(tasks.keys(), results))

        # ========== ДАННЫЕ TEMPERATURE API ==========
        temp_api_healthy = bool(result_dict.get("temp_api_health"))
        temperature_readings = []
        temp_api_info = {}

        if temp_api_healthy:
            temperature_readings, temp_api_info = await collect_temperature_api_data(session)
        else:
            logger.warning("⚠️ Temperature API is offline")

        logger.info(f"🌡️ Temperature API: {len(temperature_readings)} readings total")

        # ========== ДАННЫЕ SENSOR SERVICE ==========
        sensor_sensors_data = result_dict.get("sensor_sensors", [])
        if isinstance(sensor_sensors_data, list):
            all_sensors = sensor_sensors_data
        elif isinstance(sensor_sensors_data, dict):
            all_sensors = sensor_sensors_data.get("sensors", [])
        else:
            all_sensors = []

        logger.info(f"📊 Collected {len(all_sensors)} total sensors from Sensor Service")

        # Фильтруем датчики температуры
        temperature_sensors = [
            {
                "sensor_id": s.get("sensorId", s.get("sensor_id", "unknown")),
                "name": f"{s.get('location', 'unknown').replace('_', ' ').title()} Temperature",
                "location": s.get("location", "unknown"),
                "value": s.get("value", 0),
                "unit": s.get("unit", "°C"),
                "status": s.get("status", "active"),
                "timestamp": s.get("timestamp", datetime.now().isoformat())
            }
            for s in all_sensors
            if s.get("sensorType", s.get("sensor_type")) == "temperature"
        ]

        # Сводки по локациям
        summaries = {}
        locations = set(s.get("location") for s in temperature_sensors)
        for location in locations:
            loc_sensors = [s for s in temperature_sensors if s["location"] == location]
            if loc_sensors:
                temps = [s["value"] for s in loc_sensors]
                summaries[location] = {
                    "average_temperature": round(sum(temps) / len(temps), 1),
                    "min_temperature": round(min(temps), 1),
                    "max_temperature": round(max(temps), 1),
                    "sensor_count": len(loc_sensors),
                    "last_updated": datetime.now().isoformat()
                }

        # ========== ДАННЫЕ HEATING DEVICE ==========
        heating_healthy = bool(result_dict.get("heating_health"))
        heating_info = result_dict.get("heating_info", {})
        heating_status = result_dict.get("heating_status", {})
        heating_temp = result_dict.get("heating_temp", {})

        # ========== ФОРМИРУЕМ КЭШ ==========
        new_cache = {
            "timestamp": datetime.now().isoformat(),
            "services": {
                "temperature_api": {
                    "healthy": temp_api_healthy,
                    "info": temp_api_info if isinstance(temp_api_info, dict) else {},
                    "readings": temperature_readings[:10],
                    "readings_count": len(temperature_readings),
                    "locations": list(set(r.get("location") for r in temperature_readings)) if temperature_readings else []
                },
                "sensor_service": {
                    "healthy": bool(result_dict.get("sensor_health")),
                    "info": result_dict.get("sensor_info", {}) if isinstance(result_dict.get("sensor_info"), dict) else {},
                    "sensor_count": len(temperature_sensors),
                    "total_sensors": len(all_sensors),
                    "sensors": temperature_sensors[:10]
                },
                "heating_device": {
                    "healthy": heating_healthy,
                    "info": heating_info if isinstance(heating_info, dict) else {},
                    "status": heating_status if isinstance(heating_status, dict) else {},
                    "temperature": heating_temp if isinstance(heating_temp, dict) else {}
                }
            },
            "summaries": summaries,
            "all_sensors_count": len(all_sensors),
            "sensor_types": list(set(
                s.get("sensorType", s.get("sensor_type"))
                for s in all_sensors
                if s.get("sensorType") or s.get("sensor_type")
            ))
        }

        return new_cache

async def update_cache():
    while True:
        try:
            global cache
            new_data = await collect_all_data()
            cache.update(new_data)
            logger.info(f"✅ Cache updated at {cache['timestamp']}")
        except Exception as e:
            logger.error(f"❌ Cache update failed: {e}")
        await asyncio.sleep(5)

@app.on_event("startup")
async def startup():
    logger.info("🚀 Starting dashboard...")
    try:
        new_data = await collect_all_data()
        cache.update(new_data)
        logger.info("✅ Initial cache populated")
    except Exception as e:
        logger.error(f"❌ Initial cache failed: {e}")
    asyncio.create_task(update_cache())

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "data": cache})

@app.get("/api/data")
async def get_data():
    return cache

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8085, log_level="info")