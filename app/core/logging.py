import logging
import json
import sys
 
class JSONFormatter(logging.Formatter):
   def format(self, record: logging.LogRecord) -> str:
       log = {
           "timestamp": self.formatTime(record),
           "level": record.levelname,
           "name": record.name,
           "message": record.getMessage()   
              }
       return json.dumps(log)
    
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    return logger

