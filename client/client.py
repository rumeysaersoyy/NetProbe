# client.py
import sys
import os
# Proje ana dizinini Python'un modül arama yoluna ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import socket
import json
import base64
import os
import time
from protokol.constants import SERVER_IP, SERVER_PORT, CHUNK_SIZE, MAX_RETRIES, TIMEOUT_VAL
from protokol.packet import create_packet
from protokol.reliability import log_event

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(TIMEOUT_VAL)
server_addr = (SERVER_IP, SERVER_PORT)

sent_packets = 0
retransmissions = 0

def send_with_reliability(packet):
    global retransmissions
    retries = 0
    seq = packet["seq"]
    p_type = packet["type"]
    # Paketin ham byte boyutunu hesapla (grafiklerde throughput için gerekecek)
    packet_bytes = json.dumps(packet).encode()
    packet_size = len(packet_bytes)
    # Sadece verinin (payload) boyutunu hesapla (goodput için gerekecek)
    payload_size = len(base64.b64decode(packet["data"])) if packet["data"] else 0

    while retries < MAX_RETRIES:
        try:
            client.sendto(packet_bytes, server_addr)
            print(f"[{p_type}] Gönderildi seq={seq} (Deneme {retries+1})")
            
            # Olayı logla (DATA gönderimi)
            log_event("client_log.csv", p_type, seq, packet_size, f"SEND_TRY_{retries+1}")

            ack_data, _ = client.recvfrom(4096)
            ack = json.loads(ack_data.decode())

            if ack.get("type") == "ACK" and ack.get("seq") == seq:
                print(f"✔ ACK alındı seq={seq}")
                # Başarılı ACK logla
                log_event("client_log.csv", "ACK_RCV", seq, len(ack_data), "SUCCESS")
                return True
        except socket.timeout:
            retries += 1
            retransmissions += 1
            print(f"⏱ TIMEOUT seq={seq} → Yeniden deneniyor ({retries}/{MAX_RETRIES})")
            # Timeout olayını logla
            log_event("client_log.csv", "TIMEOUT", seq, 0, f"RETRY_{retries}")

    print(f"❌ FAIL: seq={seq} paket iletilemedi!")
    log_event("client_log.csv", "FAILED", seq, 0, "CRITICAL")
    return False

# ---------------- DOSYA GÖNDERİMİ ----------------
file_path = "client/test_files/test.txt"
if not os.path.exists(file_path):
    print(f"Hata: {file_path} bulunamadı!")
    exit()

seq = 0
start_time = time.time()

with open(file_path, "rb") as f:
    while True:
        chunk = f.read(CHUNK_SIZE)
        if not chunk:
            break

        data_b64 = base64.b64encode(chunk).decode()
        packet = create_packet("DATA", seq, data_b64)
        
        success = send_with_reliability(packet)
        if not success:
            break

        seq += 1
        sent_packets += 1

# END PAKETİ
end_packet = create_packet("END", seq)
send_with_reliability(end_packet)

print("\n--- CLIENT İSTATİSTİKLERİ ---")
print(f"Toplam Özgün Paket Sayısı: {sent_packets}")
print(f"Yeniden Gönderim (Retransmission): {retransmissions}")
client.close()