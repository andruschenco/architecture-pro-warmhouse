from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from .api import router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Создание приложения FastAPI
app = FastAPI(
    title="Heating Device Service",
    description="Микросервис для управления универсальным отопительным устройством",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Событие при запуске приложения"""
    logging.info("Heating Device Service starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """Событие при остановке приложения"""
    logging.info("Heating Device Service shutting down...")


@app.get("/", include_in_schema=False)
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Heating Device Service API",
        "docs": "/docs",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8083,
        reload=True,
        log_level="info"
    )