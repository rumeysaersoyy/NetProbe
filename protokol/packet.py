# protokol/packet.py
import json
import hashlib

def create_packet(packet_type, seq, data_b64=""):
    """Veri veya ACK paketi oluşturur ve checksum hesaplar."""
    packet = {
        "type": packet_type, # "DATA", "ACK", "END"
        "seq": seq,
        "data": data_b64
    }
    # Basit ve etkili bir checksum/hash mekanizması
    packet_bytes = f"{packet_type}:{seq}:{data_b64}".encode()
    packet["checksum"] = hashlib.md5(packet_bytes).hexdigest()
    return packet

def verify_packet(packet):
    """Paketin yolda bozulup bozulmadığını kontrol eder."""
    try:
        received_checksum = packet.get("checksum")
        packet_bytes = f"{packet.get('type')}:{packet.get('seq')}:{packet.get('data','')}".encode()
        expected_checksum = hashlib.md5(packet_bytes).hexdigest()
        return received_checksum == expected_checksum
    except Exception:
        return False