import logging
import sys
from pathlib import Path


BASE_DIR = Path(__file__).parent

LOG_FILE = BASE_DIR / "app.log"


formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S"
)


console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)


file_handler = logging.FileHandler("app.log", encoding="utf-8")
file_handler.setFormatter(formatter)


logger = logging.getLogger("monitoring_logger")
logger.setLevel(logging.INFO)


logger.addHandler(console_handler)
logger.addHandler(file_handler)
