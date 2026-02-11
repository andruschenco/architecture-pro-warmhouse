package com.sensor.service.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.UUID;

@Configuration
public class AppConfig {

    @Bean
    public String serviceId() {
        // Генерируем уникальный ID для каждого экземпляра сервиса
        return "sensor-service-" + UUID.randomUUID().toString().substring(0, 8);
    }
}