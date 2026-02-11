from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class DeviceStatus(BaseModel):
    """Модель статуса устройства"""
    device_id: str
    name: str = "Универсальное отопительное устройство"
    is_on: bool = False
    setpoint_temperature: float = 22.0  # Температура уставки по умолчанию
    current_temperature: Optional[float] = None  # Текущая температура (эмулируемая)
    power_level: int = Field(ge=0, le=100, default=0)  # Уровень мощности 0-100%
    mode: str = "auto"  # auto, manual, eco
    last_updated: datetime = datetime.now()
    version: str = "1.0.0"


class TemperatureRequest(BaseModel):
    """Модель для установки температуры"""
    temperature: float = Field(gt=10, lt=30, description="Температура должна быть между 10 и 30 градусами")


class DeviceControl(BaseModel):
    """Модель для управления устройством"""
    power: bool  # True - включить, False - выключить


class ModeRequest(BaseModel):
    """Модель для установки режима работы"""
    mode: str = Field(pattern="^(auto|manual|eco)$")


class PowerLevelRequest(BaseModel):
    """Модель для установки уровня мощности"""
    power_level: int = Field(ge=0, le=100)