# Этап сборки
FROM maven:3.9.6-eclipse-temurin-11 AS builder

WORKDIR /app

# Копируем файлы зависимостей
COPY pom.xml .
RUN mvn dependency:go-offline

# Копируем исходный код
COPY src ./src

# Собираем приложение
RUN mvn clean package -DskipTests

# Этап выполнения
FROM eclipse-temurin:11-jre-alpine

WORKDIR /app

# Устанавливаем времяzone
RUN apk add --no-cache tzdata
ENV TZ=Europe/Moscow

# Копируем собранный JAR из этапа сборки
COPY --from=builder /app/target/*.jar app.jar

# Создаем non-root пользователя для безопасности
RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring

# Открываем порт
EXPOSE 8082

# Запускаем приложение
ENTRYPOINT ["java", "-jar", "app.jar"]