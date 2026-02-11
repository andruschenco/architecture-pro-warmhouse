package com.sensor.service.model;

public enum SensorType {
    TEMPERATURE("temperature", "°C", 15.0, 30.0),
    HUMIDITY("humidity", "%", 30.0, 80.0),
    CO2("co2", "ppm", 400.0, 2000.0);

    private final String type;
    private final String unit;
    private final double minValue;
    private final double maxValue;

    SensorType(String type, String unit, double minValue, double maxValue) {
        this.type = type;
        this.unit = unit;
        this.minValue = minValue;
        this.maxValue = maxValue;
    }

    public String getType() { return type; }
    public String getUnit() { return unit; }
    public double getMinValue() { return minValue; }
    public double getMaxValue() { return maxValue; }
}