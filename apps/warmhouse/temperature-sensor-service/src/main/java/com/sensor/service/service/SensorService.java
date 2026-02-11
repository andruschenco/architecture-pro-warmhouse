package com.sensor.service.service;

import com.sensor.service.model.SensorData;
import com.sensor.service.model.SensorType;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@Service
public class SensorService {

    @Value("${service.id}")
    private String serviceId;

    // Хранилище для данных датчиков
    private final Map<String, SensorData> sensorDataMap = new ConcurrentHashMap<>();

    // Локации для датчиков
    private final List<String> locations = Arrays.asList(
            "living_room", "bedroom", "kitchen", "bathroom", "office"
    );

    public SensorService() {
        initializeSensors();
    }

    private void initializeSensors() {
        Random random = new Random();

        for (SensorType sensorType : SensorType.values()) {
            for (String location : locations) {
                String sensorId = String.format("%s-%s-%s",
                        sensorType.getType(), location, UUID.randomUUID().toString().substring(0, 4));

                double value = sensorType.getMinValue() +
                        (sensorType.getMaxValue() - sensorType.getMinValue()) * random.nextDouble();

                SensorData sensorData = new SensorData();
                sensorData.setSensorId(sensorId);
                sensorData.setSensorType(sensorType.getType());
                sensorData.setLocation(location);
                sensorData.setValue(Math.round(value * 10.0) / 10.0); // округляем до 1 знака
                sensorData.setUnit(sensorType.getUnit());
                sensorData.setTimestamp(LocalDateTime.now());
                sensorData.setStatus("active");

                sensorDataMap.put(sensorId, sensorData);
            }
        }
    }

    // Обновляем значения датчиков каждые 30 секунд
    @Scheduled(fixedRate = 30000)
    public void updateSensorValues() {
        Random random = new Random();

        for (SensorData sensorData : sensorDataMap.values()) {
            SensorType sensorType = SensorType.valueOf(sensorData.getSensorType().toUpperCase());

            // Небольшое случайное изменение (±2% от диапазона)
            double range = sensorType.getMaxValue() - sensorType.getMinValue();
            double change = (random.nextDouble() - 0.5) * range * 0.02;
            double newValue = sensorData.getValue() + change;

            // Ограничиваем значения диапазоном
            newValue = Math.max(sensorType.getMinValue(),
                    Math.min(sensorType.getMaxValue(), newValue));

            sensorData.setValue(Math.round(newValue * 10.0) / 10.0);
            sensorData.setTimestamp(LocalDateTime.now());

            // Рандомно меняем статус (95% active, 5% warning)
            if (random.nextDouble() > 0.95) {
                sensorData.setStatus("warning");
            } else {
                sensorData.setStatus("active");
            }
        }
    }

    public List<SensorData> getAllSensors() {
        return new ArrayList<>(sensorDataMap.values());
    }

    public SensorData getSensorById(String sensorId) {
        return sensorDataMap.get(sensorId);
    }

    public List<SensorData> getSensorsByType(String type) {
        return sensorDataMap.values().stream()
                .filter(sensor -> sensor.getSensorType().equalsIgnoreCase(type))
                .collect(Collectors.toList()); // Исправлено
    }

    public List<SensorData> getSensorsByLocation(String location) {
        return sensorDataMap.values().stream()
                .filter(sensor -> sensor.getLocation().equalsIgnoreCase(location))
                .collect(Collectors.toList()); // Исправлено
    }

    public Map<String, Object> getServiceInfo() {
        Map<String, Object> info = new HashMap<>();
        info.put("serviceId", serviceId);
        info.put("serviceName", "Temperature Sensor Service");
        info.put("version", "1.0.0");
        info.put("totalSensors", sensorDataMap.size());
        info.put("sensorTypes", Arrays.stream(SensorType.values())
                .map(SensorType::getType)
                .collect(Collectors.toList())); // Исправлено
        info.put("availableLocations", locations);
        info.put("timestamp", LocalDateTime.now());

        return info;
    }

    // Получаем сводные данные по всем датчикам в локации
    public Map<String, Object> getLocationSummary(String location) {
        List<SensorData> locationSensors = getSensorsByLocation(location);

        if (locationSensors.isEmpty()) {
            return Map.of("error", "No sensors found for location: " + location);
        }

        Map<String, Object> summary = new HashMap<>();
        summary.put("location", location);
        summary.put("totalSensors", locationSensors.size());
        summary.put("timestamp", LocalDateTime.now());

        Map<String, Map<String, Object>> byType = new HashMap<>();

        for (SensorData sensor : locationSensors) {
            byType.computeIfAbsent(sensor.getSensorType(), k -> {
                Map<String, Object> typeData = new HashMap<>();
                typeData.put("unit", sensor.getUnit());
                typeData.put("values", new ArrayList<Double>());
                return typeData;
            });

            @SuppressWarnings("unchecked")
            List<Double> values = (List<Double>) byType.get(sensor.getSensorType()).get("values");
            values.add(sensor.getValue());
        }

        // Рассчитываем средние значения
        Map<String, Double> averages = new HashMap<>();
        for (Map.Entry<String, Map<String, Object>> entry : byType.entrySet()) {
            @SuppressWarnings("unchecked")
            List<Double> values = (List<Double>) entry.getValue().get("values");
            double average = values.stream()
                    .mapToDouble(Double::doubleValue)
                    .average()
                    .orElse(0.0);
            averages.put(entry.getKey(), Math.round(average * 10.0) / 10.0);
        }

        summary.put("averages", averages);
        summary.put("sensors", byType);

        return summary;
    }
}