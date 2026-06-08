# server.py
import sys
import os
# Proje ana dizinini Python'un modül arama yoluna ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import socket
import json
import base64
import random
import time
from protokol.constants import SERVER_IP, SERVER_PORT, LOSS_RATE
from protokol.packet import create_packet, verify_packet
from protokol.reliability import log_event

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((SERVER_IP, SERVER_PORT))

print(f"Server dinliyor... {SERVER_IP}:{SERVER_PORT}")

received_packets = {}
total_received = 0
total_dropped = 0
start_time = None

while True:
    data, addr = server.recvfrom(4096)
    packet = json.loads(data.decode())
    packet_size = len(data)

    if not verify_packet(packet):
        print("❌ Bozuk paket (Checksum Geçersiz)!")
        continue

    if start_time is None:
        start_time = time.time()

    seq = packet["seq"]
    p_type = packet["type"]

    # Yapay Paket Kaybı Simülasyonu
    if random.random() < LOSS_RATE:
        print(f"❌ DROPPED (Simüle Edildi) {p_type} seq={seq}")
        total_dropped += 1
        log_event("server_log.csv", f"{p_type}_DROP", seq, packet_size, "DROPPED")
        continue

    # END Paketi Algılama
    if p_type == "END":
        print(f"✔ END paketi alındı. Kapanıyor... seq={seq}")
        log_event("server_log.csv", "END_RCV", seq, packet_size, "SUCCESS")
        ack_packet = create_packet("ACK", seq)
        server.sendto(json.dumps(ack_packet).encode(), addr)
        break

    # Veri Paketleme ve Mükerrer Kontrolü
    if seq not in received_packets:
        payload = base64.b64decode(packet["data"])
        received_packets[seq] = payload
        total_received += 1
        print(f"✔ ALINDI DATA seq={seq}")
        log_event("server_log.csv", "DATA_RCV", seq, packet_size, "NEW")
    else:
        print(f"⚠ DUPLICATE DATA seq={seq}")
        log_event("server_log.csv", "DATA_RCV", seq, packet_size, "DUPLICATE")

    # ACK gönder
    ack_packet = create_packet("ACK", seq)
    server.sendto(json.dumps(ack_packet).encode(), addr)

# Dosyayı birleştirme
end_time = time.time()
file_data = b""
for i in sorted(received_packets.keys()):
    file_data += received_packets[i]

with open("server/received.txt", "wb") as f:
    f.write(file_data)

print("\n--- SUNUCU PERFORMANS ÖZETİ ---")
print(f"Başarıyla Alınan Özgün Paket: {total_received}")
print(f"Düşürülen/Kaybolan Paket: {total_dropped}")
print(f"Toplam Geçen Süre: {end_time - start_time:.4f} saniye")
server.close()