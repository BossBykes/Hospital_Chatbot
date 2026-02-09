import os


class BaseConfig:
    HOSPITAL_NAME = os.getenv("HOSPITAL_NAME", "City Hospital")
    HOSPITAL_ADDRESS = os.getenv("HOSPITAL_ADDRESS", "123 Main St")
    HOSPITAL_PHONE = os.getenv("HOSPITAL_PHONE", "+1 555 0100")
    EMERGENCY_NUMBER = os.getenv("EMERGENCY_NUMBER", "911")
    CURRENCY = os.getenv("CURRENCY", "USD")
    SHOW_SOURCES = os.getenv("SHOW_SOURCES", "0")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "app/data/app.db")
