package com.sensor.service.model;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class SensorData {
    private String sensorId;
    private String sensorType;
    private String location;
    private Double value;
    private String unit;
    private LocalDateTime timestamp;
    private String status;

    public SensorData(String sensorType, String location, Double value) {
        this.sensorType = sensorType;
        this.location = location;
        this.value = value;
        this.timestamp = LocalDateTime.now();
    }
}