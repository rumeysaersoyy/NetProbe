# main.py
import sys
import os
# Proje ana dizinini Python'un modül arama yoluna ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import subprocess
import sys
import time
import os

def print_menu():
    print("\n" + "="*50)
    print(" 🚀 NETPROBE: UDP GÜVENİLİR DOSYA AKTARIM SİSTEMİ")
    print("="*50)
    print("1. Sadece Sunucuyu (Server) Başlat")
    print("2. Sadece İstemciyi (Client) Başlat")
    print("3. Performans Analizini (Grafik) Çalıştır")
    print("4. TAM SİMÜLASYON (Server -> Client -> Analiz)")
    print("0. Çıkış")
    print("="*50)

def run_full_simulation():
    print("\n[+] Tam simülasyon başlatılıyor...")
    
    # 1. Sunucuyu arka planda başlat
    print("[+] Sunucu dinlemeye alınıyor...")
    server_process = subprocess.Popen([sys.executable, "server/server.py"])
    time.sleep(1)  # Sunucunun portu açması için kısa bir bekleme
    
    # 2. İstemciyi başlat ve bitmesini bekle
    print("[+] İstemci dosya aktarımına başlıyor...\n")
    subprocess.run([sys.executable, "client/client.py"])
    
    # 3. Sunucunun dosyayı kaydedip kapanmasını bekle
    server_process.wait()
    
    # 4. Aktarım bittiğinde analiz grafiklerini otomatik çiz
    print("\n[+] Aktarım tamamlandı. Loglar analiz ediliyor...")
    subprocess.run([sys.executable, "analysis/analyzer.py"])
    print("\n✅ Simülasyon başarıyla tamamlandı!")

def main():
    # Log ve test klasörlerinin varlığından emin ol
    os.makedirs("logs", exist_ok=True)
    os.makedirs("server", exist_ok=True)
    
    while True:
        print_menu()
        secim = input("Lütfen bir işlem seçin (0-4): ")

        if secim == "1":
            print("\n[+] Sunucu başlatılıyor... (Kapatmak için Ctrl+C)")
            subprocess.run([sys.executable, "server/server.py"])
        elif secim == "2":
            print("\n[+] İstemci başlatılıyor...")
            subprocess.run([sys.executable, "client/client.py"])
        elif secim == "3":
            print("\n[+] Analiz başlatılıyor...")
            subprocess.run([sys.executable, "analysis/analyzer.py"])
        elif secim == "4":
            run_full_simulation()
        elif secim == "0":
            print("Çıkış yapılıyor. İyi çalışmalar!")
            break
        else:
            print("❌ Hatalı seçim, lütfen tekrar deneyin.")

if __name__ == "__main__":
    main()