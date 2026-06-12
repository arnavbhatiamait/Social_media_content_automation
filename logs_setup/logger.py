import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
if not os.path.exists("logs"):
     os.makedirs("logs")
class Logger:
    _instance = {}
    def __new__(cls, name='app_logger', log_file='logs/app.log', max_bytes=5*1024*1024, backup_count=2):
        if name not in cls._instance:
         cls._instance[name] = super(Logger, cls).__new__(cls)
        return cls._instance[name]
    def __init__(self, name, log_file, max_bytes=5*1024*1024, backup_count=2, level=logging.INFO):
        self.name=name
        if hasattr(self, 'logger'):
            return
        self._initialized=True
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        if not self.logger.hasHandlers():
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    def get_logger(self):
        return self.logger