-- init/init.sql
-- Этот файл выполнится автоматически при первом запуске контейнера
-- НЕ используйте команды psql (\c, \dt и т.д.) - только чистый SQL!
-- Скрипты в /docker-entrypoint-initdb.d/ выполняются только при первом запуске (когда база данных инициализируется впервые)
-- Если volume уже существует - PostgreSQL пропускает этап инициализации

-- Таблица sensors
CREATE TABLE IF NOT EXISTS sensors (
                                       id SERIAL PRIMARY KEY,
                                       name VARCHAR(100) NOT NULL,
                                       type VARCHAR(50) NOT NULL,
                                       location VARCHAR(100) NOT NULL,
                                       value FLOAT DEFAULT 0,
                                       unit VARCHAR(20),
                                       status VARCHAR(20) NOT NULL DEFAULT 'inactive',
                                       last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                                       created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_sensors_type ON sensors(type);
CREATE INDEX IF NOT EXISTS idx_sensors_location ON sensors(location);
CREATE INDEX IF NOT EXISTS idx_sensors_status ON sensors(status);
CREATE INDEX IF NOT EXISTS idx_sensors_last_updated ON sensors(last_updated);

-- Тестовые данные (опционально)
INSERT INTO sensors (name, type, location, value, unit, status)
VALUES
    ('Living Room Temperature', 'temperature', 'living_room', 22.5, '°C', 'active'),
    ('Kitchen Humidity', 'humidity', 'kitchen', 45.0, '%', 'active'),
    ('Bedroom Motion', 'motion', 'bedroom', 0, 'boolean', 'inactive')
ON CONFLICT DO NOTHING;

--
CREATE TABLE IF NOT EXISTS device_logs (
                                           id SERIAL PRIMARY KEY,
                                           sensor_id INTEGER REFERENCES sensors(id) ON DELETE CASCADE,
                                           event_type VARCHAR(50) NOT NULL,
                                           event_value TEXT,
                                           created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);