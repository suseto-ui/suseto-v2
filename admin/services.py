from .models import db, SystemLog, SystemConfig
from datetime import datetime

import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from .models import db, GlobalScan
from datetime import datetime

UPLOAD_FOLDER = '/home/Suseto/suseto_v2/uploads/scans'
MAX_IMAGE_DIMENSION = 800  # Maximální šířka/výška v px
JPEG_QUALITY = 60          # Kvalita komprese (1-100)

def process_and_save_image(image_file):
    """
    Zmenší obrázek, převede ho do stupňů šedi a uloží ho s vysokou kompresí.
    Vrací název uloženého souboru.
    """
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.jpg"
    image_path = os.path.join(UPLOAD_FOLDER, filename)

    # Otevření obrázku pomocí Pillow
    img = Image.open(image_file)
    
    # 1. Převod do stupňů šedi (Grayscale)
    img = img.convert('L')
    
    # 2. Zmenšení se zachováním poměru stran (pouze pokud je větší než limit)
    img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)
    
    # 3. Uložení s kompresí
    img.save(image_path, 'JPEG', quality=JPEG_QUALITY, optimize=True)
    
    return filename

def log_scan(scan_type, raw_data, parsed_json=None, image_file=None, ip_address=None):
    filename = None
    if image_file:
        try:
            filename = process_and_save_image(image_file)
        except Exception as e:
            print(f"Chyba při zpracování obrázku: {str(e)}")

    new_scan = GlobalScan(
        timestamp=datetime.utcnow(),
        scan_type=scan_type,
        raw_data=raw_data,
        parsed_json=parsed_json,
        image_filename=filename,
        ip_address=ip_address
    )
    db.session.add(new_scan)
    db.session.commit()
    return new_scan.id

def get_config_value(key, default=None):
    config = SystemConfig.query.filter_by(key=key).first()
    if config:
        return config.value
    return default
