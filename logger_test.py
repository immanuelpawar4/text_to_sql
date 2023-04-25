import logging
import os
from datetime import datetime

LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
curr_dir = os.path.join(os.getcwd())
logs_path = "\\".join(curr_dir.split("\\")[:-1]) + "\\logs"
os.makedirs(logs_path, exist_ok=True)

LOG_FILE_PATH = os.path.join(logs_path, "logs.log")

logging.basicConfig(

    filename = LOG_FILE_PATH,
    format = "[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level = logging.INFO,

)

if __name__ == "__main__":

    logging.error("Logging has started")

