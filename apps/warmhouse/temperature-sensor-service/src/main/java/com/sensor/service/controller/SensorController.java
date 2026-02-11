package com.sensor.service.controller;

import com.sensor.service.model.SensorData;
import com.sensor.service.service.SensorService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1")
@CrossOrigin(origins = "*")
public class SensorController {

    @Autowired
    private SensorService sensorService;

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of(
                "status", "UP",
                "service", "Temperature Sensor Service"
        ));
    }

    @GetMapping("/info")
    public ResponseEntity<Map<String, Object>> getServiceInfo() {
        return ResponseEntity.ok(sensorService.getServiceInfo());
    }

    @GetMapping("/sensors")
    public ResponseEntity<List<SensorData>> getAllSensors() {
        return ResponseEntity.ok(sensorService.getAllSensors());
    }

    @GetMapping("/sensors/{sensorId}")
    public ResponseEntity<SensorData> getSensorById(@PathVariable String sensorId) {
        SensorData sensor = sensorService.getSensorById(sensorId);
        if (sensor != null) {
            return ResponseEntity.ok(sensor);
        }
        return ResponseEntity.notFound().build();
    }

    @GetMapping("/sensors/type/{type}")
    public ResponseEntity<List<SensorData>> getSensorsByType(@PathVariable String type) {
        List<SensorData> sensors = sensorService.getSensorsByType(type);
        if (!sensors.isEmpty()) {
            return ResponseEntity.ok(sensors);
        }
        return ResponseEntity.notFound().build();
    }

    @GetMapping("/sensors/location/{location}")
    public ResponseEntity<List<SensorData>> getSensorsByLocation(@PathVariable String location) {
        List<SensorData> sensors = sensorService.getSensorsByLocation(location);
        if (!sensors.isEmpty()) {
            return ResponseEntity.ok(sensors);
        }
        return ResponseEntity.notFound().build();
    }

    @GetMapping("/summary/location/{location}")
    public ResponseEntity<Map<String, Object>> getLocationSummary(@PathVariable String location) {
        return ResponseEntity.ok(sensorService.getLocationSummary(location));
    }

    @GetMapping("/temperature/{location}")
    public ResponseEntity<Map<String, Object>> getTemperatureByLocation(@PathVariable String location) {
        List<SensorData> tempSensors = sensorService.getSensorsByType("temperature").stream()
                .filter(sensor -> sensor.getLocation().equalsIgnoreCase(location))
                .collect(Collectors.toList()); // Исправлено

        if (!tempSensors.isEmpty()) {
            double average = tempSensors.stream()
                    .mapToDouble(SensorData::getValue)
                    .average()
                    .orElse(0.0);

            return ResponseEntity.ok(Map.of(
                    "location", location,
                    "temperature", Math.round(average * 10.0) / 10.0,
                    "unit", "°C",
                    "sensorCount", tempSensors.size(),
                    "timestamp", java.time.LocalDateTime.now()
            ));
        }

        return ResponseEntity.notFound().build();
    }
}