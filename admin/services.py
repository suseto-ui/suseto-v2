from .models import db, SystemLog, SystemConfig
from datetime import datetime

def log_event(level, module, message):
    try:
        new_log = SystemLog(
            level=level.upper(),
            module=module,
            message=message,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_log)
        db.session.commit()
    except Exception as e:
        print(f"FAILED TO LOG: [{level}] {module} - {message}. Error: {str(e)}")

def get_config_value(key, default=None):
    config = SystemConfig.query.filter_by(key=key).first()
    if config:
        return config.value
    return default
