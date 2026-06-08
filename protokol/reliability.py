# protokol/reliability.py
import csv
import os
import time

LOG_DIR = "logs"

def log_event(filename, event_type, seq, size=0, status="SUCCESS"):
    """
    Ağ olaylarını logs/ klasörü altında bir CSV dosyasına kaydeder.
    Metrikler: Zaman, Olay Türü (DATA/ACK/TIMEOUT/DROP), Seq No, Boyut, Durum
    """
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        
    filepath = os.path.join(LOG_DIR, filename)
    file_exists = os.path.isfile(filepath)
    
    with open(filepath, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            # CSV Başlıkları
            writer.writerow(["timestamp", "event_type", "seq", "size_bytes", "status"])
        
        writer.writerow([time.time(), event_type, seq, size, status])