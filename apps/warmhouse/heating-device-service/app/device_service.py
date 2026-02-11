import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
import random
import logging
from .models import DeviceStatus

logger = logging.getLogger(__name__)


class HeatingDeviceService:
    """Сервис управления отопительным устройством"""

    def __init__(self):
        self.device_id = f"heating-device-{uuid.uuid4().hex[:8]}"
        self.device_status = DeviceStatus(
            device_id=self.device_id,
            is_on=False,
            setpoint_temperature=22.0,
            current_temperature=20.0,  # Начальная температура
            power_level=0,
            mode="auto"
        )
        self.operation_history = []
        logger.info(f"Инициализировано отопительное устройство с ID: {self.device_id}")

    def get_device_info(self) -> DeviceStatus:
        """Получить информацию об устройстве"""
        # Эмулируем изменение текущей температуры
        self._emulate_temperature()
        self.device_status.last_updated = datetime.now()
        return self.device_status

    def set_temperature(self, temperature: float) -> DeviceStatus:
        """Установить температуру уставки"""
        old_temp = self.device_status.setpoint_temperature
        self.device_status.setpoint_temperature = round(temperature, 1)
        self.device_status.last_updated = datetime.now()

        # Записываем в историю
        self.operation_history.append({
            "timestamp": datetime.now(),
            "operation": "set_temperature",
            "old_value": old_temp,
            "new_value": temperature
        })

        # Если устройство включено, регулируем мощность
        if self.device_status.is_on:
            self._adjust_power_level()

        logger.info(f"Установлена температура уставки: {temperature}°C (было: {old_temp}°C)")
        return self.device_status

    def get_temperature(self) -> float:
        """Получить текущую температуру уставки"""
        return self.device_status.setpoint_temperature

    def turn_on(self) -> DeviceStatus:
        """Включить устройство"""
        if not self.device_status.is_on:
            self.device_status.is_on = True
            self.device_status.last_updated = datetime.now()

            # При включении устанавливаем начальную мощность
            self._adjust_power_level()

            self.operation_history.append({
                "timestamp": datetime.now(),
                "operation": "turn_on"
            })
            logger.info("Устройство включено")

        return self.device_status

    def turn_off(self) -> DeviceStatus:
        """Выключить устройство"""
        if self.device_status.is_on:
            self.device_status.is_on = False
            self.device_status.power_level = 0
            self.device_status.last_updated = datetime.now()

            self.operation_history.append({
                "timestamp": datetime.now(),
                "operation": "turn_off"
            })
            logger.info("Устройство выключено")

        return self.device_status

    def get_status(self) -> bool:
        """Получить статус устройства (включено/выключено)"""
        return self.device_status.is_on

    def set_mode(self, mode: str) -> DeviceStatus:
        """Установить режим работы"""
        old_mode = self.device_status.mode
        self.device_status.mode = mode
        self.device_status.last_updated = datetime.now()

        self.operation_history.append({
            "timestamp": datetime.now(),
            "operation": "set_mode",
            "old_value": old_mode,
            "new_value": mode
        })

        # При изменении режима регулируем мощность
        if self.device_status.is_on:
            self._adjust_power_level()

        logger.info(f"Установлен режим: {mode} (было: {old_mode})")
        return self.device_status

    def set_power_level(self, power_level: int) -> DeviceStatus:
        """Установить уровень мощности вручную"""
        if self.device_status.mode != "manual":
            self.device_status.mode = "manual"

        old_power = self.device_status.power_level
        self.device_status.power_level = power_level
        self.device_status.last_updated = datetime.now()

        self.operation_history.append({
            "timestamp": datetime.now(),
            "operation": "set_power_level",
            "old_value": old_power,
            "new_value": power_level
        })

        logger.info(f"Установлен уровень мощности: {power_level}% (было: {old_power}%)")
        return self.device_status

    def get_operation_history(self, limit: int = 10) -> list:
        """Получить историю операций"""
        return self.operation_history[-limit:] if self.operation_history else []

    def _emulate_temperature(self):
        """Эмуляция изменения текущей температуры"""
        # Базовые изменения температуры
        temp_change = 0

        if self.device_status.is_on:
            # Если устройство включено, температура растет
            temp_change = (self.device_status.power_level / 100) * 0.5
        else:
            # Если выключено, медленно остывает
            temp_change = -0.1

        # Добавляем небольшие случайные колебания
        temp_change += random.uniform(-0.05, 0.05)

        new_temp = self.device_status.current_temperature + temp_change

        # Ограничиваем разумными пределами
        self.device_status.current_temperature = max(15.0, min(30.0, new_temp))

    def _adjust_power_level(self):
        """Автоматическая регулировка мощности на основе температуры"""
        if not self.device_status.is_on or self.device_status.mode != "auto":
            return

        # ПИД-регулятор (упрощенный)
        temp_diff = self.device_status.setpoint_temperature - self.device_status.current_temperature

        if abs(temp_diff) < 0.5:
            # Температура близка к уставке
            new_power = 20
        elif temp_diff > 2:
            # Нужно сильно нагреть
            new_power = min(100, int(50 + temp_diff * 20))
        elif temp_diff > 0:
            # Нужно немного нагреть
            new_power = min(80, int(30 + temp_diff * 15))
        elif temp_diff < -2:
            # Перегрев, уменьшаем мощность
            new_power = 10
        else:
            # Небольшой перегрев
            new_power = 30

        # Плавное изменение мощности
        if abs(new_power - self.device_status.power_level) > 10:
            step = 5 if new_power > self.device_status.power_level else -5
            self.device_status.power_level += step
        else:
            self.device_status.power_level = new_power

        logger.debug(f"Автоматическая регулировка мощности: {self.device_status.power_level}% "
                     f"(разница температур: {temp_diff:.1f}°C)")