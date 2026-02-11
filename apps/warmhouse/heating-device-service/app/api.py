from fastapi import APIRouter, HTTPException
from .models import DeviceStatus, TemperatureRequest, DeviceControl, ModeRequest, PowerLevelRequest
from .device_service import HeatingDeviceService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["heating-device"])
device_service = HeatingDeviceService()


@router.get("/health", summary="Проверка здоровья сервиса")
async def health_check():
    """Проверка работоспособности сервиса"""
    return {
        "status": "healthy",
        "service": "Heating Device Service",
        "version": "1.0.0"
    }


@router.get("/info", summary="Получить информацию об устройстве")
async def get_device_info() -> DeviceStatus:
    """Получить полную информацию об устройстве"""
    return device_service.get_device_info()


@router.get("/id", summary="Получить ID устройства")
async def get_device_id():
    """Получить уникальный идентификатор устройства"""
    status = device_service.get_device_info()
    return {"device_id": status.device_id}


@router.post("/temperature", summary="Установить температуру уставки")
async def set_temperature(request: TemperatureRequest) -> DeviceStatus:
    """
    Установить целевую температуру.

    - **temperature**: Температура в градусах Цельсия (10-30°C)
    """
    try:
        return device_service.set_temperature(request.temperature)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/temperature", summary="Получить температуру уставки")
async def get_temperature():
    """Получить текущую установленную температуру"""
    return {"temperature": device_service.get_temperature()}


@router.post("/power", summary="Включить/выключить устройство")
async def control_power(request: DeviceControl) -> DeviceStatus:
    """
    Управление питанием устройства.

    - **power**: True - включить, False - выключить
    """
    if request.power:
        return device_service.turn_on()
    else:
        return device_service.turn_off()


@router.get("/status", summary="Получить статус устройства")
async def get_status():
    """Получить текущий статус устройства (включено/выключено)"""
    return {"is_on": device_service.get_status()}


@router.post("/mode", summary="Установить режим работы")
async def set_mode(request: ModeRequest) -> DeviceStatus:
    """
    Установить режим работы устройства.

    - **mode**: Режим работы (auto, manual, eco)
    """
    return device_service.set_mode(request.mode)


@router.post("/power-level", summary="Установить уровень мощности")
async def set_power_level(request: PowerLevelRequest) -> DeviceStatus:
    """
    Установить уровень мощности вручную (работает только в manual режиме).

    - **power_level**: Уровень мощности от 0 до 100%
    """
    if not device_service.get_status():
        raise HTTPException(status_code=400, detail="Устройство выключено")

    return device_service.set_power_level(request.power_level)


@router.get("/history", summary="Получить историю операций")
async def get_history(limit: int = 10):
    """
    Получить историю операций с устройством.

    - **limit**: Максимальное количество записей (по умолчанию 10)
    """
    return {"operations": device_service.get_operation_history(limit)}


@router.get("/metrics", summary="Получить метрики устройства")
async def get_metrics():
    """Получить метрики устройства для мониторинга"""
    status = device_service.get_device_info()

    return {
        "device_id": status.device_id,
        "is_on": status.is_on,
        "setpoint_temperature": status.setpoint_temperature,
        "current_temperature": status.current_temperature,
        "power_level": status.power_level,
        "mode": status.mode,
        "temperature_difference": round(status.setpoint_temperature - status.current_temperature, 1),
        "is_heating": status.current_temperature < status.setpoint_temperature,
        "energy_efficiency": "high" if status.mode == "eco" else "normal",
        "uptime_minutes": 120  # Примерное значение, можно сделать расчет
    }