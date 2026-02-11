package com.sensor.service;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class SensorServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(SensorServiceApplication.class, args);
    }
}