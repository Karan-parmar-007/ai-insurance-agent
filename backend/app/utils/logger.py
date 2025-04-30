import logging
import os
from logging.handlers import RotatingFileHandler

# Define log file path
LOG_FILE = os.path.join(os.getcwd(), "app.log")

# Create Logger
logger = logging.getLogger("mailwhatsapp")

# Set formatter
formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(module)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

# Create rotating file handler (max size 50MB, 1 backup, clear when full)
handler = RotatingFileHandler(LOG_FILE, maxBytes=50 * 1024 * 1024, backupCount=1)
handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(handler)

# Set log level based on environment
ENV_MODE = os.getenv("FLASK_ENV", "development")  # Default to 'development' if not set

if ENV_MODE == "production":
    logger.setLevel(logging.ERROR)  # Only log errors in production
else:
    logger.setLevel(logging.DEBUG)  # Log everything in development

logger.info(f"Logger initialized in {ENV_MODE} mode")
